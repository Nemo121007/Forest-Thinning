**wpd.json**
- **version**: list
  0. 4
  1. 2
- **axesColl**: list - список осей
  0. dict:
     - **name**: str - названия осей
     - **type**: str
     - **isLogX**: bool - метка логарифмической шкалы для оси X
     - **isLogY**: bool - метка логарифмической шкалы для оси X
     - **noRotation**: bool - метка отсутствия поворота
     - **calibrationPoints**: list - список точек для построения осей
       0. dict: - первая точка для построения осей
          - **px**: float - координата по X относительно графика
          - **py**: float - координата по Y относительно графика
          - **dx**: str - координата по X (в пикселях) относительно изображения 
          - **dy**: str - координата по Y (в пикселях) относительно изображения 
          - **dz**: dz - - координата по Z относительно изображения 
       1. dict - вторая точка для построения осей
       2. dict - третья точка для построения осей
       3. dict - четвертая точка для построения осей
- **datasetColl**: list - список графиков
  0. dict: - первый график
     - **name**: str - название графика
     - **axesName**: str - название осей, по которым строится график
     - **colorRGB**: list - цвет графика
       0. int
       1. int
       2. int
       3. int
     - **metadataKeys**: list
     - **data**: list - список точек графика
       0. dict:
          - **x**: float
          - **y**: float
          - **value**: list:
            0. float - значение по оси x для графика
            1. float - значение по оси y для графика
       1. dict
       2. dict
     - **autoDetectionData**: dict - параметры, связанные с автоматическим распознаванием графика
       - **fgColor**: list
         0. int
         1. int
         2. int
       - **bgColor**: list
         0. int
         1. int
         2. int
       - **mask**: list
         0. list:
            - int
            - int
         1. list
       - **colorDetectionMode**: str
       - **colorDistance**: int
       - **algorithm**: dict
         0. **algoType**: str
         1. **xStep**: int
         2. **yStep**: int
       - **name**: int
       - **imageWidth**: int
       - **imageHeight**
  1. dict - второй график
- **measurementColl**: list 