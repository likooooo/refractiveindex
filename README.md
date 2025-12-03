##
基于 [refractiveindex](https://github.com/toftul/refractiveindex) 修改的版本

- 材料库 page 按照时间由近到远进行排序
``` bash
python3 ./sort_pages.py
```

- 下载材料库
``` bash
python3 ./download_material.py
```

- 导出材料 nk
``` bash
python3 ./download_material.py Ag > Ag.txt
```

- 导出材料 nk 并绘制 f(wave_length) = nk 的曲线
``` bash
python3 ./download_material.py --plot Ag > Ag.txt
```

- 注意事项  
download_material.py 采用默认策略自动选择 sheet 和 page.   
默认策略是获取表格中第一组测量结果。  
如果在使用了 sort_pages.py 后, 默认获取时间最近的测量结果。
