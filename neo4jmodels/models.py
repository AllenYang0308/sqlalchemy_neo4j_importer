from neo4jmodels.base.fields import Field
from neo4jmodels.base.models import Model


class Customer(Model):
    fullname = Field("FullName")
    age = Field("Age")
    idcode = Field("IDCode")


class CustomerOther(Model):
    name = Field("Name")
    idcode = Field("IDCode")
