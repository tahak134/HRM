from pydantic import BaseModel, Field
from bson import ObjectId
from pydantic_core import core_schema

# 1. This is the modern, Pydantic v2 way to handle ObjectIds.
# It tells Pydantic how to validate and serialize the type.
class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source, _handler):
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema(),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

# 2. This is the corrected base model for all your responses.
class MongoModel(BaseModel):
    # It correctly uses PyObjectId for the 'id' field.
    id: PyObjectId = Field(default=None, alias="_id")

    class Config:
        # This tells Pydantic to read data from object attributes (e.g., goal._id)
        from_attributes = True 
        # This allows the use of the '_id' alias
        populate_by_name = True
        # This is good practice when working with custom types
        arbitrary_types_allowed = True
