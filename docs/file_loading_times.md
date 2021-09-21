# Some loading time studies

```python
>>> %timeit events.arrays(entry_stop=1000)
29 ms ± 355 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

>>> %timeit events.arrays(entry_stop=100_000)
1.74 s ± 117 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

>>> %timeit events.arrays(entry_stop=1000, library="pandas")
238 ms ± 2.75 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

>>> %timeit events.arrays(entry_stop=100_000, library="pandas")
1min ± 3.86 s per loop (mean ± std. dev. of 7 runs, 1 loop each)
```
