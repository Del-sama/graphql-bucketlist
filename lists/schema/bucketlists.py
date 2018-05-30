from datetime import date

import graphene
from graphene_django import DjangoObjectType

from graphql import GraphQLError

from django.db.models import Q
from django.contrib.auth import get_user_model

from ..models import Bucketlist
from user.schema import UserType


class BucketlistType(DjangoObjectType):
    class Meta:
        model = Bucketlist


class CreateBucketlist(graphene.Mutation):
    id = graphene.Int()
    name = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        name = graphene.String()

    def mutate(self, info, name):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You mused be logged in!")
        bucketlist = Bucketlist(name=name, user=user)
        bucketlist.save()

        return CreateBucketlist(
            id=bucketlist.id,
            name=bucketlist.name,
            user=bucketlist.user
        )


class UpdateBucketlist(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        bucketlist_id = graphene.Int(required=True)
        name = graphene.String()

    def mutate(self, info, bucketlist_id, name):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You mused be logged in!")

        bucketlist = Bucketlist.objects.get(id=bucketlist_id)
        if user.id != bucketlist.user_id:
            return GraphQLError("Not authorized")

        try:
            bucketlist.name = name
            bucketlist.updated_at = date.today()
            bucketlist.save()
            return UpdateBucketlist(message="Bucketlist successfully updated!")
        except Bucketlist.DoesNotExist:
            return GraphQLError("Bucketlist does not exist")


class DeleteBucketlist(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        bucketlist_id = graphene.Int(required=True)

    def mutate(self, info, bucketlist_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You mused be logged in!")

        if user.id != bucketlist.user_id:
            return GraphQLError("Not authorized")

        try:
            bucketlist = Bucketlist.objects.get(id=bucketlist_id)
            bucketlist.delete()
            return DeleteBucketlist(message="Bucketlist successfully deleted!")
        except Bucketlist.DoesNotExist:
            return GraphQLError("Bucketlist does not exist")


class Query(graphene.ObjectType):
    bucketlists = graphene.List(
        BucketlistType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int()
        )
    bucketlist = graphene.Field(BucketlistType, bucketlist_id=graphene.Int())
    user_bucketlists = graphene.List(
        BucketlistType,
        user_id=graphene.Int(),
        first=graphene.Int(),
        skip=graphene.Int()
        )

    def resolve_bucketlists(self, info, search=None, first=None, skip=None, **kwargs):
        bucketlists = Bucketlist.objects.all()
        if search:
            filter = (
                Q(name__icontains=search)
            )
            bucketlists = bucketlists.filter(filter)

        if skip:
            bucketlists = bucketlists[skip::]

        if first:
            bucketlists = bucketlists[:first]

        return bucketlists

    def resolve_bucketlist(self, info, bucketlist_id):
        try:
            return Bucketlist.objects.get(id=bucketlist_id)
        except Bucketlist.DoesNotExist:
            raise GraphQLError("Bucketlist does not exist")

    def resolve_user_bucketlists(self, info, user_id, first=None, skip=None, **kwargs):
        user = get_user_model().objects.get(id=user_id)

        if user:
            bucketlists = Bucketlist.objects.filter(user_id=user_id)
            if skip:
                bucketlists = bucketlists[skip::]

            if first:
                bucketlists = bucketlists[:first]

            return bucketlists
        else:
            raise GraphQLError("User does not exist")


class Mutation(graphene.ObjectType):
    create_bucketlist = CreateBucketlist.Field()
    update_bucketlist = UpdateBucketlist.Field()
    delete_Bucketlist = DeleteBucketlist.Field()
