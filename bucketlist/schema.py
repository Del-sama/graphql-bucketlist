import graphene
import graphql_jwt
import user.schema
from lists.schema import bucketlists, items


class Query(user.schema.Query, bucketlists.Query, items.Query, graphene.ObjectType):
    pass


class Mutation(user.schema.Mutation, bucketlists.Mutation, items.Mutation, graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
