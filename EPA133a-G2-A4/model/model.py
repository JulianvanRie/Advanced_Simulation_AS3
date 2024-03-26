import networkx as nx
from mesa import Model, DataCollector
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from components import Source, Sink, SourceSink, Bridge, Link, Intersection
import pandas as pd
from collections import defaultdict
import math as math
import mesa


# ---------------------------------------------------------------
def set_lat_lon_bound(lat_min, lat_max, lon_min, lon_max, edge_ratio=0.02):
    """
    Set the HTML continuous space canvas bounding box (for visualization)
    give the min and max latitudes and Longitudes in Decimal Degrees (DD)

    Add white borders at edges (default 2%) of the bounding box
    """

    lat_edge = (lat_max - lat_min) * edge_ratio
    lon_edge = (lon_max - lon_min) * edge_ratio

    x_max = lon_max + lon_edge
    y_max = lat_min - lat_edge
    x_min = lon_min - lon_edge
    y_min = lat_max + lat_edge
    return y_min, y_max, x_min, x_max


# ---------------------------------------------------------------
class BangladeshModel(Model):
    """
    The main (top-level) simulation model

    One tick represents one minute; this can be changed
    but the distance calculation need to be adapted accordingly

    Class Attributes:
    -----------------
    step_time: int
        step_time = 1 # 1 step is 1 min

    path_ids_dict: defaultdict
        Key: (origin, destination)
        Value: the shortest path (Infra component IDs) from an origin to a destination

        Only straight paths in the Demo are added into the dict;
        when there is a more complex network layout, the paths need to be managed differently

    sources: list
        all sources in the network

    sinks: list
        all sinks in the network

    """

    step_time = 1

    file_name = '../data/merged_data.csv'

    def __init__(self, scenario_probabilities, seed=None, x_max=500, y_max=500, x_min=0, y_min=0):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []
        self.bridges = []
        self.scenario_probabilities = scenario_probabilities
        self.generate_model()
        self.generate_network()


    def get_scenario_probabilities(self):
        return self.scenario_probabilities

    def generate_network(self):
        self.G = nx.Graph()  # Initialize the Graph attribute of the class

        # Read the CSV file
        data = pd.read_csv(self.file_name)

        # Add nodes with positions
        for idx, row in data.iterrows():
            self.G.add_node(row['id'], pos=(row['lon'], row['lat']), label=row['name'], weight=0)
            if row['model_type'] == 'bridge':
               for bridge in self.bridges:
                   if row['id'] == bridge.unique_id:
                        vehicle_speed = 48 * 1000 / 60 / 1000
                        self.G.nodes[row['id']]['weight'] = bridge.delay_time * vehicle_speed  # is now in km

        # Add edges for sequential nodes within the same road
        roads = data.groupby('road')
        for road_name, group in roads:
            sorted_group = group.sort_values(by='id')  # Ensure nodes are added sequentially
            for i in range(len(sorted_group) - 1):
                if math.isnan(sorted_group.iloc[i]['length']):
                    self.G.add_edge(sorted_group.iloc[i]['id'], sorted_group.iloc[i + 1]['id'],
                                    weight=0.2)  # this is the specific bridge Narayanpur Bridge which has a NaN, we looked up the length on google
                    # print(self.G.edges[(sorted_group.iloc[i]['id'], sorted_group.iloc[i + 1]['id'])])
                else:
                    self.G.add_edge(sorted_group.iloc[i]['id'], sorted_group.iloc[i + 1]['id'], weight=sorted_group.iloc[i]['length'])


        # Handle intersections: connect the end of one road to the start of another if they have the same name in the description
        for idx, row in data.iterrows():
            if 'intersection' in row['model_type'].lower():
                self.G.add_edge(row['id'], row['intersects_with'], weight=0)

        for u, v, d in self.G.edges(data=True):

            node_u_weight = self.G.nodes[u].get('weight', 0)
            d['weight'] += node_u_weight

    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels
        """
        df = pd.read_csv(self.file_name)

        # a list of names of roads to be generated
        # TODO You can also read in the road column to generate this list automatically
        roads = ['N1', 'N102', 'N104', 'N105', 'N106', 'N2', 'N204', 'N207', 'N208']

        df_objects_all = []
        for road in roads:
            # Select all the objects on a particular road in the original order as in the cvs
            df_objects_on_road = df[df['road'] == road]

            if not df_objects_on_road.empty:
                df_objects_all.append(df_objects_on_road)
        #
        #         """
        #         Set the path
        #         1. get the serie of object IDs on a given road in the cvs in the original order
        #         2. add the (straight) path to the path_ids_dict
        #         3. put the path in reversed order and reindex
        #         4. add the path to the path_ids_dict so that the vehicles can drive backwards too
        #         """
        #         path_ids = df_objects_on_road['id']
        #         path_ids.reset_index(inplace=True, drop=True)
        #         self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
        #         self.path_ids_dict[path_ids[0], None] = path_ids
        #         path_ids = path_ids[::-1]
        #         path_ids.reset_index(inplace=True, drop=True)
        #         self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
        #         self.path_ids_dict[path_ids[0], None] = path_ids

        # put back to df with selected roads so that min and max and be easily calculated
        df = pd.concat(df_objects_all)
        y_min, y_max, x_min, x_max = set_lat_lon_bound(
            df['lat'].min(),
            df['lat'].max(),
            df['lon'].min(),
            df['lon'].max(),
            0.05
        )

        # ContinuousSpace from the Mesa package;
        # not to be confused with the SimpleContinuousModule visualization
        self.space = ContinuousSpace(x_max, y_max, True, x_min, y_min)

        for df in df_objects_all:
            for _, row in df.iterrows():  # index, row in ...

                # create agents according to model_type
                model_type = row['model_type'].strip()
                agent = None

                name = row['name']
                if pd.isna(name):
                    name = ""
                else:
                    name = name.strip()

                if model_type == 'source':
                    agent = Source(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                elif model_type == 'sink':
                    agent = Sink(row['id'], self, row['length'], name, row['road'])
                    self.sinks.append(agent.unique_id)
                elif model_type == 'sourcesink':
                    agent = SourceSink(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                    self.sinks.append(agent.unique_id)
                elif model_type == 'bridge':
                    agent = Bridge(row['id'], self, row['length'], name, row['road'], row['condition'])
                    self.bridges.append(agent)
                elif model_type == 'link':
                    agent = Link(row['id'], self, row['length'], name, row['road'])
                elif model_type == 'intersection':
                    if not row['id'] in self.schedule._agents:
                        agent = Intersection(row['id'], self, row['length'], name, row['road'])

                if agent:
                    self.schedule.add(agent)
                    y = row['lat']
                    x = row['lon']
                    self.space.place_agent(agent, (x, y))
                    agent.pos = (x, y)
        Source.truck_counter = 0

    def get_random_route(self, source):
        """
        pick up a random route given an origin
        """
        while True:
            # different source and sink
            sink = self.random.choice(self.sinks)
            if sink is not source:
                break
        return self.get_shortest_path(source, sink)

    def get_shortest_path(self, source, destination):
        """
        Returns the shortest path between the source and destination, checks if it's already there or calculates it.
        """
        # print(f'Starting making a shortest path between {source} and {destination}')
        if (source, destination) in self.path_ids_dict:
            # print('the if statement triggered')
            return self.path_ids_dict[(source, destination)]

        #calculate shortest path with networkx
        # print('I reached point 1')
        path = nx.shortest_path(self.G, source=source, target=destination, weight='weight')
        path_series = pd.Series(path)
        # print('I reached point 2')
        total_weight = 0
        for i in range(len(path) - 1):
            edge_weight = self.G[path[i]][path[i + 1]]['weight']
            total_weight += edge_weight
        # print(f"Total weight of the path {path[0], path[-1]}, length {len(path)}: {total_weight}")
        #store the computed path
        # print(f'I made a path here between {source} and {destination}')
        self.path_ids_dict[(source, destination)] = path_series

        return path_series

    # TODO
    def get_route(self, source):
        return self.get_random_route(source)

    def get_straight_route(self, source):
        """
        pick up a straight route given an origin
        """
        return self.path_ids_dict[source, None]

    def step(self):
        """
        Advance the simulation by one step.
        """
        self.schedule.step()


# EOF -----------------------------------------------------------
def get_bridge_data(model):
    bridge_data = []
    for agent in model.schedule.agents:
        if isinstance(agent, Bridge):
            bridge_data.append({
                "unique_id": agent.unique_id,
                "condition": agent.condition,
                "total_delay_time": agent.total_delay_time,
                "delay_time": agent.delay_time,
                "break_down_chance": agent.break_down_chance,
                "breaks_down": agent.breaks_down
            })
    return bridge_data