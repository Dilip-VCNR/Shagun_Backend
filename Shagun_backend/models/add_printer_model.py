from dataclasses import dataclass
from typing import Any, TypeVar, Type, cast


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class AddPrinterModel:
    store_name: str
    city: int
    address: str
    lat_lng: str
    gst_no: str
    store_owner: str
    contact_number: str
    printer_user_name: str
    printer_password: str

    @staticmethod
    def from_dict(obj: Any) -> 'AddPrinterModel':
        assert isinstance(obj, dict)
        store_name = from_str(obj.get("store_name"))
        city = from_int(obj.get("city"))
        address = from_str(obj.get("address"))
        lat_lng = from_str(obj.get("lat_lng"))
        gst_no = from_str(obj.get("gst_no"))
        store_owner = from_str(obj.get("store_owner"))
        contact_number = from_str(obj.get("contact_number"))
        printer_user_name = from_str(obj.get("printer_user_name"))
        printer_password = from_str(obj.get("printer_password"))
        return AddPrinterModel(store_name, city, address, lat_lng, gst_no, store_owner, contact_number, printer_user_name, printer_password)

    def to_dict(self) -> dict:
        result: dict = {}
        result["store_name"] = from_str(self.store_name)
        result["city"] = from_int(self.city)
        result["address"] = from_str(self.address)
        result["lat_lng"] = from_str(self.lat_lng)
        result["gst_no"] = from_str(self.gst_no)
        result["store_owner"] = from_str(self.store_owner)
        result["contact_number"] = from_str(self.contact_number)
        result["printer_user_name"] = from_str(self.printer_user_name)
        result["printer_password"] = from_str(self.printer_password)
        return result


def add_printer_model_from_dict(s: Any) -> AddPrinterModel:
    return AddPrinterModel.from_dict(s)


def add_printer_model_to_dict(x: AddPrinterModel) -> Any:
    return to_class(AddPrinterModel, x)
