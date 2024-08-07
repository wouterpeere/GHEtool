***************
Load data
***************

GHEtool supports different types of load data (and more are coming, check our project for more information: https://github.com/users/wouterpeere/projects/2)
Currently you can use:

#. Geothermal loads with a monthly resolution for one year (so it repeats itself every year)
#. Geothermal loads with an hourly resolution for one year (so it repeats itself every year)
#. Geothermal loads with an monthly resolution but multiple years (it does not repeat itself)
#. Geothermal loads with an hourly resolution but multiple years (it does not repeat itself)

All of the load classes are based children of the abstract _LoadData class.

.. automodule:: GHEtool.VariableClasses.Baseclasses._SingleYear
    :members:
    :show-inheritance:
    :private-members:

.. automodule:: GHEtool.VariableClasses.Baseclasses._MonthlyData
    :members:
    :show-inheritance:
    :private-members:

.. automodule:: GHEtool.VariableClasses.Baseclasses._HourlyData
    :members:
    :show-inheritance:
    :private-members:

.. automodule:: GHEtool.VariableClasses.LoadData.GeothermalLoad.MonthlyGeothermalLoadAbsolute
    :members:
    :show-inheritance:

.. automodule:: GHEtool.VariableClasses.LoadData.GeothermalLoad.HourlyGeothermalLoad
    :members:
    :show-inheritance:

.. automodule:: GHEtool.VariableClasses.LoadData.GeothermalLoad.MonthlyGeothermalLoadMultiYear
    :members:
    :show-inheritance:

.. automodule:: GHEtool.VariableClasses.LoadData.GeothermalLoad.HourlyGeothermalLoadMultiYear
    :members:
    :show-inheritance:
