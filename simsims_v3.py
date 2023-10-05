"""Revised version of simsims assignment"""

import random
from queue import Queue
from queue import LifoQueue
import time
import json
import matplotlib.image as mpimg
import matplotlib.pyplot as plt


class World():
    """World class"""

    def __init__(self):
        self.transitions = {"Factory": [],
                            "Field": [], "Home": [], "Canteen": []}
        self.places = {"Barrack": [], "Warehouse": [], "Barn": []}

    def create_places(self, place_type: str, amount: int):
        """Method for creating an amount of places of a certain type"""
        for i in range(amount):
            if place_type == "Barrack":
                self.places["Barrack"].append(Barrack())
            elif place_type == "Warehouse":
                self.places["Warehouse"].append(Warehouse())
            elif place_type == "Barn":
                self.places["Barn"].append(Barn())

    def random_place(self, place_type: str):
        """Method for randomly selecting a place of a certain type"""
        return self.places[place_type][random.randint(0, len(self.places[place_type]) - 1)]

    def create_transitions(self, transition_type: str, amount: int):
        """Method for creating an amount of transitions of a certain type"""
        for i in range(amount):
            if transition_type == "Factory":
                self.transitions["Factory"].append(Factory(self.random_place(
                    "Barrack"), self.random_place("Barrack"), self.random_place("Warehouse")))
            elif transition_type == "Field":
                self.transitions["Field"].append(Fields(self.random_place(
                    "Barrack"), self.random_place("Barrack"), self.random_place("Barn")))
            elif transition_type == "Home":
                self.transitions["Home"].append(Home(self.random_place(
                    "Barrack"), self.random_place("Barrack"), self.random_place("Warehouse")))
            elif transition_type == "Canteen":
                self.transitions["Canteen"].append(Canteen(self.random_place(
                    "Barrack"), self.random_place("Barrack"), self.random_place("Barn")))

    def create_life(self):
        """Method that creates a number of workers equal to the number of barracks,
         but randomly assigns them to barracks."""
        for i in range(len(self.places["Barrack"])):
            self.places["Barrack"][random.randint(
                0, len(self.places["Barrack"]) - 1)].add_resource(Worker())

    def setup(self, num_barracks: int, num_warehouses: int, num_barns: int,
              num_factories: int, num_fields: int, num_homes: int, num_canteens: int):
        """Method that initializes the world"""
        self.create_places("Barrack", num_barracks)
        self.create_places("Warehouse", num_warehouses)
        self.create_places("Barn", num_barns)
        self.create_transitions("Factory", num_factories)
        self.create_transitions("Field", num_fields)
        self.create_transitions("Home", num_homes)
        self.create_transitions("Canteen", num_canteens)
        self.create_life()

    def optimal_from_place(self, key: str):
        """Finds the optimal place to take a resource from"""
        highest = 0
        optimal_from_place = self.places[key][0]
        for place in self.places[key]:
            if place.resources_in_place() > highest:
                highest = place.resources_in_place()
                optimal_from_place = place

        return optimal_from_place

    def find_highest_population(self, key: str):
        """Finds the highest population of a certain place type"""
        highest_population = 0
        for place in self.places[key]:
            if place.resources_in_place() > highest_population:
                highest_population = place.resources_in_place()

        return highest_population

    def optimal_to_place(self, key: str):
        """Finds the optimal place to send a resource to"""
        lowest = self.find_highest_population(key)
        optimal_to_place = self.places[key][0]
        for place in self.places[key]:
            if place.resources_in_place() <= lowest:
                lowest = place.resources_in_place()
                optimal_to_place = place

        return optimal_to_place

    def total_population(self, key: str):
        """Returns total population of resources in a type of place"""
        total = 0
        for place in self.places[key]:
            total += place.resources_in_place()

        return total

    def run(self):
        """Runs a "day" in the world"""

        current_factory_index = 0
        current_field_index = 0
        available_factories = True
        available_fields = True
        # For each worker in a barrack, determine what needs to be produced and produce it in a optimal way
        for worker in range(self.total_population("Barrack")):
            # If food is prioritized over products
            if self.optimal_from_place("Barn").resources_in_place() <= self.optimal_from_place("Warehouse").resources_in_place() and available_fields:
                if current_field_index > len(self.transitions["Field"]) - 1:
                    available_fields = False
                    break
                field = self.transitions["Field"][current_field_index]
                # Optimize where it gets workers from
                field.change_from_place(
                    self.optimal_from_place("Barrack"))
                field.change_to_place(self.optimal_to_place("Barrack"))
                field.barn = self.optimal_to_place("Barn")

                if field.from_place.has_resource():
                    field.produce()

                current_field_index += 1

            else:  # Products are prioritized over food
                if current_factory_index > (len(self.transitions["Factory"]) - 1) or not available_factories:
                    available_factories = False
                    break
                factory = self.transitions["Factory"][current_factory_index]
                # Optimize where it gets workers from
                factory.change_from_place(
                    self.optimal_from_place("Barrack"))
                factory.change_to_place(
                    self.optimal_to_place("Barrack"))
                factory.warehouse = self.optimal_to_place("Warehouse")

                if factory.from_place.has_resource():
                    factory.produce()

                current_factory_index += 1

        choice = random.choice([1, 2])
        if choice == 1:
            # All canteens take workers and give them food
            for canteen in self.transitions["Canteen"]:
                # Optimize where it gets workers and food from
                canteen.change_from_place(self.optimal_from_place("Barrack"))
                canteen.change_to_place(self.optimal_to_place("Barrack"))
                canteen.barn = self.optimal_from_place("Barn")

                if canteen.from_place.has_resource():
                    canteen.produce()
        elif choice == 2:
            # All homes take workers and give them products
            for home in self.transitions["Home"]:
                # Optimize where it gets workers and products from
                home.change_from_place(self.optimal_from_place("Barrack"))
                home.change_to_place(self.optimal_to_place("Barrack"))
                home.warehouse = self.optimal_from_place("Warehouse")

                if home.from_place.has_resource():
                    home.produce()

    def should_run(self):
        """Checks if the world should keep running"""
        for barrack in self.places["Barrack"]:
            if barrack.resources_in_place() > 0:
                return True
        return False

    def genocide(self):
        """Kills everyone"""
        for barrack in self.places["Barrack"]:
            for i in range(barrack.resources_in_place()):
                worker = barrack.send_resource()
                worker.destroy()


class StatisticsHandler():
    def __init__(self, world: World):
        self.world = world
        self.days = []
        self.workers = []
        self.products = []
        self.foods = []

    def save_json(self, current_cycle: int):
        workers = 0
        products = 0
        foods = 0
        for barrack in self.world.places["Barrack"]:
            workers += barrack.resources_in_place()
        for warehouse in self.world.places["Warehouse"]:
            products += warehouse.resources_in_place()
        for barn in self.world.places["Barn"]:
            foods += barn.resources_in_place()

        self.days.append(current_cycle)
        self.workers.append(workers)
        self.products.append(products)
        self.foods.append(foods)

        data = {"days": self.days, "workers": self.workers,
                "products": self.products, "foods": self.foods}

        with open("data.json", "w") as save:
            json.dump(data, save)

    def make_csv(self):
        """Makes a csv file of the data"""
        with open("data.json", "r") as save:
            data = json.load(save)

        with open("data.csv", "w") as csv:
            csv.write("days,workers,products,foods\n")
            for i in range(len(data["days"])):
                csv.write(str(data["days"][i]) + "," + str(data["workers"][i]) + "," +
                          str(data["products"][i]) + "," + str(data["foods"][i]) + "\n")

    def make_png(self):
        """Makes a png file of the data"""
        with open("data.json", "r") as save:
            data = json.load(save)

        plt.plot(data["days"], data["workers"], label="Workers")
        plt.plot(data["days"], data["products"], label="Products")
        plt.plot(data["days"], data["foods"], label="Foods")
        plt.xlabel("Days")
        plt.ylabel("Amount")
        plt.legend()
        plt.savefig("graph.png")

    def display_stats(self):
        """Show png file"""
        png = mpimg.imread("graph.png")
        plt.show()


class Resource():
    """Parent class for all resources"""

    def __init__(self):
        pass

    def destroy(self):
        del self


class Worker(Resource):
    def __init__(self):
        self.health = 100
        super().__init__()

    def is_alive(self):
        if self.health > 0:
            return True
        return False


class Place():
    """Parent class for all places"""

    def __init__(self, queue):
        self.queue = queue

    def has_resource(self):
        if self.queue.empty():
            return False
        return True

    def resources_in_place(self):
        return self.queue.qsize()

    def add_resource(self, resource):
        self.queue.put(resource)

    def send_resource(self):
        if not self.queue.empty():
            return self.queue.get()


class Transition():
    """Parent class for all transitions"""

    def __init__(self, to_place, from_place):
        self.to_place = to_place
        self.from_place = from_place

    def modify_worker_health(self, worker: Worker, modifier: int):
        worker.health += modifier
        if worker.health > 100:
            worker.health = 100

    def change_from_place(self, new_place: Place):
        self.from_place = new_place

    def change_to_place(self, new_place: Place):
        self.to_place = new_place


class Barrack(Place):
    """Where workers reside when not out on gig. (FIFO)"""

    def __init__(self):
        self.workers = Queue()
        super().__init__(self.workers)


class Product(Resource):
    """Somehow makes workers reproduce"""

    def __init__(self):
        super().__init__()


class Food(Resource):
    """Resource workers consume in order to get health"""

    def __init__(self):
        self.quality = random.randint(25, 100)
        super().__init__()


class Warehouse(Place):
    """Storage location for products (LIFO)"""

    def __init__(self):
        self.products = LifoQueue()
        super().__init__(self.products)


class Barn(Place):
    """Storage location for food (FIFO)"""

    def __init__(self):
        self.foods = Queue()
        super().__init__(self.foods)


class Factory(Transition):
    """Turns "labor" into products"""

    def __init__(self, to_barrack, from_barrack, warehouse):
        super().__init__(to_barrack, from_barrack)
        self.warehouse = warehouse
        self.danger_level = random.randint(1, 20)

    def produce(self):
        worker = self.from_place.send_resource()
        if worker is not None:
            produced = Product()
            self.modify_worker_health(worker, self.danger_level)
            self.warehouse.add_resource(produced)
            if worker.is_alive():
                self.to_place.add_resource(worker)
            else:
                worker.destroy()


class Fields(Transition):
    """Turns "labor" into food"""

    def __init__(self, to_barrack, from_barrack, barn):
        self.barn = barn
        self.accident_risk = random.choice([1, 3, 5, 5, 10, 15])
        super().__init__(to_barrack, from_barrack)

    def produce(self):
        worker = self.from_place.send_resource()
        if worker is not None:
            produced = Food()
            if random.randint(1, 100) <= self.accident_risk:
                self.modify_worker_health(worker, random.randint(-20, -5))
            self.barn.add_resource(produced)
            if worker.is_alive():
                self.to_place.add_resource(worker)
            else:
                del worker


class Home(Transition):
    """Turns product and  two workers into one more workers 
    or gives a single worker health """

    def __init__(self, to_barrack, from_barrack, warehouse):
        self.warehouse = warehouse
        super().__init__(to_barrack, from_barrack)

    def produce(self):
        worker1 = self.from_place.send_resource()
        worker2 = self.from_place.send_resource()
        product = self.warehouse.send_resource()

        if worker1 and worker2 and product is not None:
            self.to_place.add_resource(worker1)
            self.to_place.add_resource(worker2)
            self.to_place.add_resource(Worker())
            del product
        elif worker1 and product is not None and worker2 is None:
            self.to_place.add_resource(worker1)
            self.modify_worker_health(worker1, 10)
            del product
        else:
            if worker1 is not None:
                self.from_place.add_resource(worker1)
            if worker2 is not None:
                self.from_place.add_resource(worker2)
            if product is not None:
                self.warehouse.add_resource(product)


class Canteen(Transition):
    """Turns a food and a worker into extra health for the worker. 
    If food quality is too bad it may harm the worker instead."""

    def __init__(self, to_barrack, from_barrack, barn):
        self.barn = barn
        super().__init__(to_barrack, from_barrack)

    def produce(self):
        worker = self.from_place.send_resource()
        food = self.barn.send_resource()
        if worker is not None and food is not None:
            if food.quality >= 50:
                self.modify_worker_health(worker, 10)
            elif food.quality < 50:
                self.modify_worker_health(worker, -15)
            if worker.is_alive():
                self.to_place.add_resource(worker)
            else:
                del worker
            food.destroy()
        else:  # If there is no worker or food, return them to their respective places
            if worker is not None:
                self.from_place.add_resource(worker)
            if food is not None:
                self.barn.add_resource(food)


if __name__ == "__main__":
    game_world = World()
    stats = StatisticsHandler(game_world)
    game_world.setup(8, 1, 1, 2, 2, 8, 1)
    cycle = 0
    running = True
    while running and cycle < 200:
        game_world.run()
        if not game_world.should_run():
            running = False
        stats.save_json(cycle)
        cycle += 1
        # time.sleep(1)

    total_food = 0
    for barn in game_world.places["Barn"]:
        total_food += barn.resources_in_place()
    print(total_food)

    stats.make_csv()
    stats.make_png()
    stats.display_stats()
    print("Simulation Over")
