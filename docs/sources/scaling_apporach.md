# Scaling profile approach

The scaling profile approach is scaling the original profile ({math}`P_{original}^t`) of the current time step ({math}`t`) to the scaling profile
for the selected period ({math}`P_{scaling}^{t}`). It is linearly interpolated using the scaling factor ({math}`S^{f(t)}`). 
Therefore, the scaling factor have to be assigned to the current time step. This is illustrated by {math}`f(t)`. For Example if a monthly period is considered 
the average value array has 12 entries. So one of these 12 entries has to be assigned to the current time step. All time steps in january are
referred to the first entry, all time steps in february to the second entry, and so on.

```{math}
P_{new}^t = P_{original}^t  \cdot S^{f(t)} + P_{scaling}^t \cdot \left(1 - S^{f(t)}\right)
```

The scaling factor ({math}`S^{k}`) can either be provided by the user or calculated based on the simultaneity factor ({math}`SF`). 
This is determined by an algorithm which minimizes the error of the scaling factor time the maximum value for the current period and
the maximum of scaled profile.

As periods can be selected a daily (1), a weekly (2), a monthly (3) or a yearly (4) one. An example code is shown below:

```{literalinclude} ../../examples/example_scaling.py
:language: python
:linenos:
:caption:
```