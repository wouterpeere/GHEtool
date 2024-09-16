import numpy as np

from GHEtool.VariableClasses.LoadData.Baseclasses._LoadData import _LoadData


class Cluster:

    def __init__(self, buildings: list[_LoadData] = []):
        """
        Parameters
        ----------
        buildings : list of _LoadData

        Returns
        -------
        None
        """
        self.__dict__['list_of_buildings'] = buildings  # Avoid recursion with __setattr__

    def add_building(self, building: _LoadData):
        """
        This function adds a building to the cluster.

        Parameters
        ----------
        building : _LoadData

        Returns
        -------
        None
        """
        self.list_of_buildings.append(building)

    def __getattr__(self, attr_name):
        """
        Intercepts any method call that doesn't exist in Cluster and forwards it to all buildings.

        Parameters
        ----------
        attr_name : str
            The name of the method to be applied to each building.

        Returns
        -------
        function
            A function that applies the method to all buildings and sums the result.
        """

        if callable(getattr(self.list_of_buildings[0], attr_name, None)):
            def method_applier(*args, **kwargs):
                results = []
                for building in self.list_of_buildings:
                    method = getattr(building, attr_name)
                    result = method(*args, **kwargs)
                    if result is not None:  # pragma: no cover
                        results.append(result)
                return np.sum(results, axis=0)

            return method_applier
        else:
            return np.sum([getattr(building, attr_name) for building in self.list_of_buildings], axis=0)

    def __setattr__(self, attr_name, value):
        """
        Sets an attribute on all buildings in the cluster.

        Parameters
        ----------
        attr_name : str
            The name of the attribute to be set.
        value :
            The value to set for the attribute.
        """
        for building in self.list_of_buildings:
            setattr(building, attr_name, value)
