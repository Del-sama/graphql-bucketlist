from datetime import date
import graphene
from graphene_django import DjangoObjectType

from graphql import GraphQLError

from django.db.models import Q

from ..models import Bucketlist, Item
from .bucketlists import BucketlistType


class ItemType(DjangoObjectType):
    class Meta:
        model = Item


class CreateItem(graphene.Mutation):
    id = graphene.Int()
    title = graphene.String()
    bucketlist = graphene.Field(BucketlistType)

    class Arguments:
        bucketlist_id = graphene.Int()
        title = graphene.String()

    def mutate(self, info, title, bucketlist_id):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You must be logged in!")

        bucketlist = Bucketlist.objects.filter(id=bucketlist_id).first()
        if not bucketlist:
            raise GraphQLError("Invalid bucketlist")

        item = Item(title=title, bucketlist=bucketlist)
        item.save()

        return CreateItem(
            id=item.id,
            title=item.title,
            bucketlist=item.bucketlist
        )


class UpdateItem(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        item_id = graphene.Int(required=True)
        title = graphene.String()
        done = graphene.Boolean()

    def mutate(self, info, item_id, title=None, done=None):
        user = info.context.user
        if user.is_anonymous:
            raise GraphQLError("You mused be logged in!")

        item = Item.objects.get(id=item_id)
        if title:
            item.title = title
        if done:
            item.done = done
        item.updated_at = date.today()
        item.save()
        return UpdateItem(message="Item successfully updated!")


class DeleteItem(graphene.Mutation):
    message = graphene.String()

    class Arguments:
        item_id = graphene.Int(required=True)

    def mutate(self, info, item_id):
        try:
            item = Item.objects.get(id=item_id)
            item.delete()
            return DeleteItem(message="Item successfully deleted!")
        except Item.DoesNotExist:
            return GraphQLError("Item does not exist")


class Query(graphene.ObjectType):
    items = graphene.List(
        ItemType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int()
        )
    item = graphene.Field(ItemType, item_id=graphene.Int())

    def resolve_items(self, info, search=None, first=None, skip=None, **kwargs):
        items = Item.objects.all()

        if search:
            filter = (
                Q(title__icontains=search)
            )
            return items.filter(filter)

        if skip:
            items = items[skip::]

        if first:
            items = items[:first]

        return items

    def resolve_item(self, info, item_id):
        try:
            return Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return GraphQLError("Item does not exist")


class Mutation(graphene.ObjectType):
    create_item = CreateItem.Field()
    update_item = UpdateItem.Field()
    delete_item = DeleteItem.Field()
