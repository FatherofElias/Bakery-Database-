import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import InventoryItem as InventoryItemModel, db

class InventoryItem(SQLAlchemyObjectType):
    class Meta:
        model = InventoryItemModel
        interfaces = (graphene.relay.Node,)

class CreateInventoryItem(graphene.Mutation):
    class Arguments:
        product_name = graphene.String(required=True)
        price = graphene.Float(required=True)
        quantity = graphene.Int(required=True)
        category = graphene.String(required=True)

    inventory_item = graphene.Field(lambda: InventoryItem)

    def mutate(self, info, product_name, price, quantity, category):
        item = InventoryItemModel(product_name=product_name, price=price, quantity=quantity, category=category)
        db.session.add(item)
        db.session.commit()
        return CreateInventoryItem(inventory_item=item)

class UpdateInventoryItem(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        product_name = graphene.String()
        price = graphene.Float()
        quantity = graphene.Int()
        category = graphene.String()

    inventory_item = graphene.Field(lambda: InventoryItem)

    def mutate(self, info, id, product_name=None, price=None, quantity=None, category=None):
        item = InventoryItemModel.query.get(id)
        if item is None:
            raise Exception('Inventory item not found')

        if product_name:
            item.product_name = product_name
        if price:
            item.price = price
        if quantity:
            item.quantity = quantity
        if category:
            item.category = category

        db.session.commit()
        return UpdateInventoryItem(inventory_item=item)

class DeleteInventoryItem(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        item = InventoryItemModel.query.get(id)
        if item is None:
            raise Exception('Inventory item not found')

        db.session.delete(item)
        db.session.commit()
        return DeleteInventoryItem(ok=True)

class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    all_inventory_items = SQLAlchemyConnectionField(InventoryItem.connection)
    inventory_item = graphene.Field(InventoryItem, id=graphene.Int())

    def resolve_inventory_item(self, info, id):
        return InventoryItemModel.query.get(id)

class Mutation(graphene.ObjectType):
    create_inventory_item = CreateInventoryItem.Field()
    update_inventory_item = UpdateInventoryItem.Field()
    delete_inventory_item = DeleteInventoryItem.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
