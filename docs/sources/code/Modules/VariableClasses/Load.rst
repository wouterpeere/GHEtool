***************
Load data
***************

GHEtool supports different types of load data (and more are coming, check our project for more information: https://github.com/users/wouterpeere/projects/2)
Currently you can use:

#. Geothermal loads with a monthly resolution for one year (so it repeats itself every year)
#. Geothermal loads with an hourly resolution for one year (so it repeats itself every year)
#. Geothermal loads with an hourly resolution but multiple years (it does not repeat itself)

All of the load classes are based children of the abstract _LoadData class.

.. automodule:: GHEtool.VariableClasses.LoadData._LoadData
    :members:
    :show-inheritance:
    :private-members:

.. automodule:: GHEtool.VariableClasses.GeothermalLoad.MonthlyGeothermalLoadAbsolute
    :members:
    :show-inheritance:

.. automodule:: GHEtool.VariableClasses.GeothermalLoad.HourlyGeothermalLoad
    :members:
    :show-inheritance:

.. automodule:: GHEtool.VariableClasses.GeothermalLoad.HourlyGeothermalLoadMultiYear
    :members:
    :show-inheritance:
