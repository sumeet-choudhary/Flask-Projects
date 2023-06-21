from flask_sqlalchemy import BaseQuery
from app.utils import msg_result
from flask import url_for, request
from app.extensions import db
from flask_restful import Resource, abort, Mapping, ResponseBase
from flask_restful.utils import http_status_message, unpack, OrderedDict
from sqlalchemy import and_

DEFAULT_PAGE_SIZE = 50
DEFAULT_PAGE_NUMBER = 1


class ResourceMixin(Resource):
    model_class = None
    schema_class = None
    filter_backends = []
    permission_classes = []
    ordering = ['-create_time', ]

    # request = None
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def dispatch_request(self, *args, **kwargs):

        # Taken from flask
        # noinspection PyUnresolvedReferences
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, 'Unimplemented method %r' % request.method

        if isinstance(self.method_decorators, Mapping):
            decorators = self.method_decorators.get(request.method.lower(), [])
        else:
            decorators = self.method_decorators

        for decorator in decorators:
            meth = decorator(meth)

        self.check_permissions()
        resp = meth(*args, **kwargs)

        if isinstance(resp, ResponseBase):  # There may be a better way to test
            return resp

        representations = self.representations or OrderedDict()

        # noinspection PyUnresolvedReferences
        mediatype = request.accept_mimetypes.best_match(representations, default=None)
        if mediatype in representations:
            data, code, headers = unpack(resp)
            resp = representations[mediatype](data, code, headers)
            resp.headers['Content-Type'] = mediatype
            return resp

        return resp

    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.

        (Eg. return a list of items that is specific to the user)
        """
        assert self.model_class is not None, (
                "'%s' should either include a `model_class` attribute, "
                "or override the `get_queryset()` method."
                % self.__class__.__name__
        )
        queryset = self.model_class.query
        # if isinstance(queryset, BaseQuery):
        #     # Ensure queryset is re-evaluated on each request.
        #     # queryset = queryset.all()
        #     queryset = queryset
        queryset = self.fuzzy_query(queryset)  # 模糊查询
        return queryset

    def get_object(self):
        """
        Returns the object the view is displaying.

        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in request.view_args, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )
        # get_or_404
        obj = queryset.filter(
            getattr(self.model_class, lookup_url_kwarg) == request.view_args.get(lookup_url_kwarg,
                                                                                 None)).first_or_404()
        self.check_object_permissions(obj)

        return obj

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(request, queryset, self)
        return queryset

    def get_schema_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.schema_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
        )

        return self.schema_class

    def get_schema(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        schema_class = self.get_schema_class()
        return schema_class(*args, **kwargs)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in self.permission_classes]

    def check_permissions(self):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                abort(403)

    def check_object_permissions(self, obj):
        """
        Check if the request should be permitted.
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                abort(403)

    def get_ordering(self, queryset):
        """
        Return a tuple of strings, that may be used in an `order_by` method.
        """
        ordering_filters = [
            filter_cls for filter_cls in getattr(self, 'filter_backends', [])
            if hasattr(filter_cls, 'get_ordering')
        ]

        if ordering_filters:
            # If a filter exists on the view that implements `get_ordering`
            # then we defer to that filter to determine the ordering.
            filter_cls = ordering_filters[0]
            filter_instance = filter_cls()
            ordering = filter_instance.get_ordering(request, queryset, self)
            assert ordering is not None, (
                'Using cursor pagination, but filter class {filter_cls} '
                'returned a `None` ordering.'.format(
                    filter_cls=filter_cls.__name__
                )
            )
        else:
            # The default case is to check for an `ordering` attribute
            # on this pagination instance.
            ordering = self.ordering
            assert ordering is not None, (
                'Using cursor pagination, but no ordering attribute was declared '
                'on the pagination class.'
            )
            assert '__' not in ordering, (
                'Cursor pagination does not support double underscore lookups '
                'for orderings. Orderings should be an unchanging, unique or '
                'nearly-unique field on the model, such as "-created" or "pk".'
            )

        assert isinstance(ordering, (str, list, tuple)), (
            'Invalid ordering. Expected string or tuple, but got {type}'.format(
                type=type(ordering).__name__
            )
        )

        if isinstance(ordering, str):
            return (ordering,)
        return tuple(ordering)

    def _extract_pagination(self, page=None, per_page=None, **request_args):
        page = int(page) if page is not None else DEFAULT_PAGE_NUMBER
        per_page = int(per_page) if per_page is not None else DEFAULT_PAGE_SIZE
        return page, per_page, request_args

    def paginate(self, query, schema):
        page, per_page, other_request_args = self._extract_pagination(**request.args)
        ordering = self.get_ordering(query)

        ordering = [
            getattr(self.model_class, field[1:]).desc() if field.startswith("-") else getattr(self.model_class,
                                                                                              field) for field in
            ordering]
        query = query.order_by(*ordering)
        page_obj = query.paginate(page=page, per_page=per_page)
        next_ = url_for(
            request.endpoint,
            page=page_obj.next_num if page_obj.has_next else page_obj.page,
            per_page=per_page,
            **other_request_args,
            **request.view_args
        )
        prev = url_for(
            request.endpoint,
            page=page_obj.prev_num if page_obj.has_prev else page_obj.page,
            per_page=per_page,
            **other_request_args,
            **request.view_args
        )

        return {
            "message": "succesed",
            "total": page_obj.total,
            "pages": page_obj.pages,
            "next": next_,
            "prev": prev,
            "results": schema.dump(page_obj.items),
        }

    def msg_result(self, msg, value, stats=200):
        return {'message': msg, 'results': value}, stats

    def fuzzy_query(self, queryset):
        """模糊查询"""
        fields = self.determine_filter_fields()
        filter_data = [k.like(f'%{v}%') for k, v in fields.items()]
        query = queryset.filter(and_(*filter_data))
        return query

    def determine_filter_fields(self):
        """
        确定模糊查询的字段
        返回字段名和模糊搜索值
        {User.username: 'zzz', }
        """
        fields = {}
        get_request_fields = self.get_request_fields()
        for field in get_request_fields.keys():
            if field in self.get_filter_fields():
                fields[field] = get_request_fields[field]
        fields = {getattr(self.model_class, k): v for k, v in fields.items()}
        return fields

    @staticmethod
    def get_request_fields():
        """模糊查询上传的字段"""
        d = {k: v for k, v in request.args.items()}
        return d

    def get_filter_fields(self):
        """模糊查询定义的字段"""
        filter_fields = getattr(self, 'filter_fields', [])
        return filter_fields

    def list(self, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        # queryset = queryset.order_by(Job.create_time.desc())
        schema = self.get_schema(many=True)
        return self.paginate(queryset, schema)

    def retrieve(self, *args, **kwargs):
        instance = self.get_object()
        schema = self.get_schema()
        return self.msg_result('succesed', schema.dump(instance))

    def update(self, *args, **kwargs):
        instance = self.get_object()
        schema = self.get_schema(partial=True)
        instance = schema.load(request.json, instance=instance)
        db.session.commit()
        return self.msg_result('succesed', schema.dump(instance))

    def destroy(self, *args, **kwargs):
        instance = self.get_object()
        db.session.delete(instance)
        db.session.commit()
        return self.msg_result('succesed', {}, 204)

    def create(self, *args, **kwargs):
        schema = self.get_schema()
        instance = schema.load(request.json)
        db.session.add(instance)
        db.session.commit()
        return self.msg_result('succesed', schema.dump(instance), 201)
