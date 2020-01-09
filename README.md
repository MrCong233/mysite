# User Guide

PS: This project only support UI of Chinese language, so be careful to use in your project
## Installation
## Set Up
## Operation
## 生成图片的方法说明

1. 首先将轨迹点数据组织为(unix_timestamp, wgs84_longtitude, wgs84_latitude)，例如1477964797,104.09464,30.703971000000006。然后以csv文件的格式保存，每列数据间用英文逗号`,`隔开，没有头部header信息。
2. 第二步将csv文件放入your-project-location/mysite/rhythm/algorithm/dataset中，例如dataset1.csv
3. 第三步打开页面<http://localhost:8000/rhythm/index_to_generate_image/>
4. 第四步在页面的表单中，选择生成图片的方法，并填写第二步导入的数据集文件的名称（例如dataset1.csv），然后运行即可生成图片
   1. 注：此页面中一次只能使用一个生成图片的方法和一个数据集名称
   2. 原因是此生成图片的方法现在极不稳定，容易出现运行时异常，时常需要重启服务器，然后重新运行
5. 生成图片的地址位于your-project-location/mysite/rhythm/static/rhythm/img/generated中，图片的文件名称为“数据集名称-生成方法-所用参数.png”，例如：dataset1.csv-2d_equal_grid-10.png