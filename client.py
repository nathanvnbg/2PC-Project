
import xmlrpclib

def main():
    coordinator = xmlrpclib.Server('http://localhost:8000', allow_none=True)

    coordinator.coord_put(1, "Test1")
    coordinator.coord_put(2, "Test2")
    coordinator.coord_put(3, "Test3")
    coordinator.coord_put(4, "Test4")

    coordinator.coord_del(2)

    print coordinator.coord_get(3)


if __name__ == "__main__":
    main()
