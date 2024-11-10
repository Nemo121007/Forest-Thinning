**wpd.json**
- **version**: list
  1. 4
  2. 2
- **axesColl**: list - список осей
  1. dict:
     - **name**: str - названия осей
     - **type**: str
     - **isLogX**: bool - метка логарифмической шкалы для оси X
     - **isLogY**: bool - метка логарифмической шкалы для оси X
     - **noRotation**: bool - метка отсутствия поворота
     - **calibrationPoints**: list - список точек для построения осей
       1. dict: - первая точка для построения осей
          - **px**: float - координата по X относительно графика
          - **py**: float - координата по Y относительно графика
          - **dx**: str - координата по X (в пикселях) относительно изображения 
          - **dy**: str - координата по Y (в пикселях) относительно изображения 
          - **dz**: dz - - координата по Z относительно изображения 
       2. dict - вторая точка для построения осей
       3. dict - третья точка для построения осей
       4. dict - четвертая точка для построения осей
- **datasetColl**: list - список графиков
  1. dict: - первый график
     - **name**: str - название графика
     - **axesName**: str - название осей, по которым строится график
     - **colorRGB**: list - цвет графика
       1. int
       2. int
       3. int
       4. int
     - **metadataKeys**: list
     - **data**: list - список точек графика
       1. dict:
          - **x**: float
          - **y**: float
          - **value**: list:
            1. float - значение по оси x для графика
            2. float - значение по оси y для графика
       2. dict
     - **autoDetectionData**: dict - параметры, связанные с автоматическим распознаванием графика
       - **fgColor**: list
         1. int
         2. int
         3. int
       - **bgColor**: list
         1. int
         2. int
         3. int
       - **mask**: list
         1. list:
            - int
            - int
         2. list
       - **colorDetectionMode**: str
       - **colorDistance**: int
       - **algorithm**: dict
         1. **algoType**: str
         2. **xStep**: int
         3. **yStep**: int
       - **name**: int
       - **imageWidth**: int
       - **imageHeight**
  2. dict - второй график
- **measurementColl**: list 