***********************************************************
Inter sizing tool comparison
***********************************************************

In GHEtool v2.1.1 there are two major code changes that reduce the computational time significantly. One has to do with the way the sizing methodology (L3/L4) is implemented and another with the new Gfunction class.
Both improvements are explained below.

+++++++++++++++++++++
test 1a 
+++++++++++++++++++++
.. list-table:: Calculated borefield lengths for test 1a 
   :header-rows: 1

   * - Simulation period [years]
     - Required time old method [µs]
     - Required time new method [µs]
   * - 5 years
     - 15625 µs
     - 0 µs

.. csv-table:: Table Title
   :file: ../../../../GHEtool/Validation/comparison_with_other_sizing_tools/test1a/table1a.csv table1a
   :widths: 8,7,7,7,7,7,7,7,7,7,7,7,7,7
   :header-rows: 1
+++++++++++++++++++++
test 1b
+++++++++++++++++++++
.. list-table:: Calculated borefield lengths for test 1b
   :header-rows: 1

   * - Simulation period [years]
     - Required time old method [µs]
     - Required time new method [µs]
   * - 5 years
     - 15625 µs
     - 0 µs
+++++++++++++++++++++
test 2 
+++++++++++++++++++++
.. list-table:: Calculated borefield lengths for test 2
   :header-rows: 1

   * - Simulation period [years]
     - Required time old method [µs]
     - Required time new method [µs]
   * - 5 years
     - 15625 µs
     - 0 µs
+++++++++++++++++++++
test 3
+++++++++++++++++++++
.. list-table:: Calculated borefield lengths for test 3
   :header-rows: 1

   * - Simulation period [years]
     - Required time old method [µs]
     - Required time new method [µs]
   * - 5 years
     - 15625 µs
     - 0 µs
+++++++++++++++++++++
test 4
+++++++++++++++++++++
.. list-table:: Calculated borefield lengths for test 4
   :header-rows: 1

   * - Simulation period [years]
     - Required time old method [µs]
     - Required time new method [µs]
   * - 5 years
     - 15625 µs
     - 0 µs
+++++++++++++++++++++++++++++
sensitivity analysis test 4
+++++++++++++++++++++++++++++
.. list-table:: Calculated borefield lengths for different input parameters for test 4
   :header-rows: 1

   * - Simulation period [years]
     - Required time old method [µs]
     - Required time new method [µs]
   * - 5 years
     - 15625 µs
     - 0 µs

.. literalinclude:: ../../../../GHEtool/Validation/comparison_with_other_sizing_tools/test1a/test1a.py
   :language: python
   :linenos:

.. literalinclude:: ../../../../GHEtool/Validation/comparison_with_other_sizing_tools/test1b/test1b.py
   :language: python
   :linenos:

.. literalinclude:: ../../../../GHEtool/Validation/comparison_with_other_sizing_tools/test2/test2.py
   :language: python
   :linenos:

.. literalinclude:: ../../../../GHEtool/Validation/comparison_with_other_sizing_tools/test3/test3.py
   :language: python
   :linenos:

.. literalinclude:: ../../../../GHEtool/Validation/comparison_with_other_sizing_tools/test4/test4.py
   :language: python
   :linenos:

.. literalinclude:: ../../../../GHEtool/Validation/comparison_with_other_sizing_tools/test4/sensitivity_analysis.py
   :language: python
   :linenos:


.. rubric:: References
.. [1] Meertens, L., Peere, W., and Helsen, L. (2024). Influence of short-term dynamic effects on geothermal borefield size. In _Proceedings of International Ground Source Heat Pump Association Conference 2024_. Montr�al (Canada), 28-30 May 2024. https://doi.org/10.22488/okstate.24.000004