import graphene
from graphene_django import DjangoObjectType
from apps.users.models import User as UserModel
from apps.floaters.models import Floater as FloaterModel

class User(DjangoObjectType):
    class Meta:
        model = UserModel
        
class Floater(DjangoObjectType):
    class Meta:
        model = FloaterModel

class Query(graphene.ObjectType):
    users = graphene.List(User)
    floaters = graphene.List(Floater)

    def resolve_users(self, info, **kwargs):
        return UserModel.objects.all()
    
    def resolve_floaters(self, info, **kwargs):
        return FloaterModel.objects.all()

class ChangeFloater(graphene.Mutation):
    user = graphene.Field(User)

    class Arguments:
        floater_id = graphene.Int(required=True)

    def mutate (self, info, floater_id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        floater = FloaterModel.objects.get(id=floater_id)

        if floater.TIER_LEVELS > user.active_tier:
            raise Exception("You can't choose a floater from a higher tier")

        user.floater = floater
        user.save()

        return ChangeFloater(user=user)
        
class Mutation(graphene.ObjectType):
    change_floater = ChangeFloater.Field()
    
schema = graphene.Schema(query=Query)