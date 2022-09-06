# Normal Distribution approach

Hello World 

```{math}
ND(x, t) = \frac{e^{-0.5 \frac{\left(x - t\right)^2}{\sigma^2}}}{\sqrt{2 \cdot \pi} \cdot \sigma}
```

integration is

```{math}
NDI(x, t) = \frac{erf((x + 0.5 - t) / (\sigma \cdot \sqrt{2})) - erf((x - 0.5 - t) / (\sigma \cdot \sqrt{2}))}{2}
```

```{math}
P_{new}^t = P_{original}^t \cdot \sum_{i=t-4 \cdot \lfloor\sigma+0.5\rceil}^{t+4 \cdot \lfloor\sigma+0.5\rceil} NDI(i, t)
```

An example code is shown below:

```{literalinclude} ../../examples/example_normal_distribution.py
:language: python
:linenos:
:caption:
```