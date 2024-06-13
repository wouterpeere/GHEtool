***********************************************************
Inter sizing tool comparison
***********************************************************
Ahmadfard and Bernier (2019) developed a comprehensive set of test cases designed to compare software tools, 
ultimately aiming to enhance the reliability of design methods for sizing vertical ground heat exchangers. 
They reviewed existing tests and proposed four new test cases that cover a wide range of conditions, 
from single boreholes to extensive bore fields with varying annual ground thermal imbalances. 
They then conducted an inter-model comparison of twelve sizing tools, including several commercially available 
software programs (such as EED, GLHEpro, and DTS) and different forms of the ASHRAE sizing equation. The L2-, L3-, and L4-sizing methods of 
GHEtool were validated using this openly accessible document. 

+++++++++++++++++++++
Test 1
+++++++++++++++++++++

The first test case employs a synthetically generated balanced load profile, either as a ground load or a building load. 
This test assumes a single borehole handles the load without borehole-to-borehole thermal interference. An analysis of 
the first two sets in Test 1a shows that the various sizing tools provide results that are in relatively good agreement. 
For the first set, the borehole lengths range from 54.8 to 62.1 m. The GHEtool L2-, L3-, and L4-methods yielded lengths 
of 59.4 m (1.2% deviation), 59.6 m (1.6% deviation), and 56.3 m (-4.0% deviation), respectively. The GHEtool L4-method's 
slightly lower result is likely due to its use of hourly values instead of a 6-hour peak duration, which aligns with other 
L4 tools. The borehole thermal resistance evaluated with GHEtool was 0.128 mK/W for all methods, consistent with other 
values for this parameter. 

.. list-table:: Calculated borefield lengths for test 1a with  a peak load duration of 6 hours and Rb calculated by tool
   :header-rows: 1

   * - Sizing method [years]
     - Borehole length [m]
     - Difference from mean [%]
     - Rb calculate by tool [m.K/W]
   * - L2
     - 59.4
     - 1.2
     - 0.128
   * - L3
     - 59.6 
     - 1.6
     - 0.128
   * - L4
     - 56.3 
     - -4.0
     - 0.128
   * - mean
     - 58.2
     -
     - 0.124
   * - min
     - 54.8
     -
     - 0.120
   * - max
     - 62.1 
     - 
     - 0.128

When the same Rb value (0.13 mK/W) was used for all tools in the second set of Test 1a, the 
borehole lengths ranged from 56.5 to 63.7 m, with a mean of 59.8 m. The GHEtool L2- and L3-methods produced lengths of 
59.8 m (-0.3% deviation) and 60.0 m (0.0% deviation), respectively, while the L4-method gave a slightly shorter length 
of 56.7 m (-5.4% deviation), consistent with other L4 methods. The differences in Rb evaluation across tools in Test 1a 
were typical for all test cases, indicating no significant flaws among the tools. Therefore, the remainder of this 
validation will discuss the performance for identical values for Rb. 

.. list-table:: Calculated borefield lengths for test 1a with  a peak load duration of 6 hours and imposed Rb = 0.13 m.K/W
   :header-rows: 1

   * - Sizing method [years]
     - Borehole length [m]
     - Difference from mean [%]
     - Imposed Rb = 0.13 m.K/W [m.K/W]
   * - L2
     - 59.8
     - -0.3
     - 0.13
   * - L3
     - 60.0
     - 0.0
     - 0.13
   * - L4
     - 56.7
     - -5.4
     - 0.13
   * - mean
     - 59.8
     -
     - 
   * - min
     - 56.5
     -
     - 
   * - max
     - 63.7 
     - 
     - 
   

+++++++++++++++++++++
Test 1b
+++++++++++++++++++++
.. list-table:: Calculated borefield lengths for test 1b with  a peak load duration of 6 hours and imposed Rb = 0.13 m.K/W
   :header-rows: 1

   * - Sizing method [years]
     - Borehole length [m]
     - Difference from mean [%]
     - Imposed Rb = 0.13 m.K/W [m.K/W]
   * - L2
     - 76.7
     - 0.8
     - 0.13
   * - L3
     - 76.7
     - 0.8
     - 0.13
   * - L4
     - 72.5
     - -4.7
     - 0.13
   * - mean
     - 76.1
     -
     - 
   * - min
     - 71.3
     -
     - 
   * - max
     - 81.3
     - 
     - 
+++++++++++++++++++++
Test 2 
+++++++++++++++++++++
.. list-table:: Calculated borefield lengths for test 2 with  a peak load duration of 6 hours and imposed Rb = 0.113 m.K/W
   :header-rows: 1

   * - Sizing method [years]
     - Borehole length [m]
     - Difference from mean [%]
     - Imposed Rb = 0.113 m.K/W [m.K/W]
   * - L2
     - 77.5
     - -11.6
     - 0.113
   * - L3
     - 79.6
     - -9.1
     - 0.113
   * - L4
     - 85.0
     - -2.9
     - 0.113
   * - mean
     - 87.6
     -
     - 
   * - min
     - 77.5
     -
     - 
   * - max
     - 102.0
     - 
     - 
+++++++++++++++++++++
Test 3
+++++++++++++++++++++
.. list-table:: Calculated borefield lengths for test 3 with  a peak load duration of 6 hours and imposed Rb = 0.1 m.K/W
   :header-rows: 1

   * - Sizing method [years]
     - Borehole length [m]
     - Difference from mean [%]
     - Imposed Rb = 0.1 m.K/W [m.K/W]
   * - L2
     - 107.5
     - 6.4
     - 0.1
   * - L3
     - 107.4
     - 6.2
     - 0.1
   * - L4
     - 107.4
     - 6.2
     - 0.1
   * - mean
     - 101.1
     -
     - 
   * - min
     - 85.9
     -
     - 
   * - max
     - 115.0
     - 
     - 

.. list-table:: Calculated borefield lengths for test 3 for different spacing (B) and design period (p)
   :header-rows: 1

   * - Sizing method [years]
     - p=1 y, B=3 m
     - p=1 y, B=5 m
     - p=1 y, B=7 m
     - p=10 y, B=3 m
     - p=10 y, B=5 m
     - p=10 y, B=7 m
   * - L2
     - 113.4
     - 107.5
     - 107.1
     - 113.4
     - 107.5
     - 107.1
   * - L3
     - 118.4
     - 107.5
     - 107.1
     - 118.1
     - 107.4
     - 106.9
   * - L4
     - 114.4
     - 107.4 
     - 107.4
     - 114.1
     - 107.4
     - 108.3
   * - mean
     - 117.8
     - 110.7
     - 110.5
     - 101.2
     - 101.1
     - 104.6
   * - min
     - 105.0
     - 104.6
     - 106.3
     - 77.0
     - 85.9
     - 93.2
   * - max
     - 130.6
     - 115.0
     - 115.0
     - 130.6
     - 115.0
     - 115.0
+++++++++++++++++++++
Test 4
+++++++++++++++++++++
.. list-table:: Calculated borefield lengths for test 4 with  a peak load duration of 6 hours and imposed Rb = 0.2 m.K/W
   :header-rows: 1

   * - Sizing method [years]
     - Borehole length [m]
     - Difference from mean [%]
     - Imposed Rb = 0.2 m.K/W [m.K/W]
   * - L2
     - 121.5
     - 1.9
     - 0.2
   * - L3
     - 122.2
     - 2.5
     - 0.2
   * - L4
     - 120.0
     - 0.6
     - 0.2
   * - mean
     - 119.2
     -
     - 
   * - min
     - 93.0
     -
     - 
   * - max
     - 128.9
     - 
     - 

+++++++++++++++++++++++++++++
Sensitivity analysis test 4
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

.. [1] Ahmadfard and Bernier (2019) developed a comprehensive set of test cases designed to compare software tools, ultimately aiming to enhance the reliability of design methods for sizing vertical ground heat exchangers. They reviewed existing tests and proposed four new test cases that cover a wide range of conditions, from single boreholes to extensive bore fields with varying annual ground thermal imbalances. They then conducted an inter-model comparison of twelve sizing tools, including several commercially available software programs and different forms of the ASHRAE sizing equation. The L2-, L3-, and L4-sizing methods of GHEtool were validated using this openly accessible document. 
.. [2] Meertens, L., Peere, W., and Helsen, L. (2024). Influence of short-term dynamic effects on geothermal borefield size. In _Proceedings of International Ground Source Heat Pump Association Conference 2024_. Montr�al (Canada), 28-30 May 2024. https://doi.org/10.22488/okstate.24.000004