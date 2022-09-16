# Measuring sidewalk widths for Amsterdam

This repository contains a sidewalk width calculation approach by considering static obstacles on the sidewalk. This project is part of a broader [accessibility project](https://amsterdamintelligence.com/projects/amsterdam-for-all) to determine if [sidewalks are accessible](https://amsterdamintelligence.com/posts/accessiblesidewalkwidth) and make them more inclusive to people with disabilities. Two point cloud datasets are used in this project that were taken of the same area but at different times. First, cadastral reference data is used to filter for the points above the sidewalk. Next, a change detection algorithm, M3C2, is used to identify static objects in the point clouds. Finally, sidewalk width is calculated, inspired by Meli Harvey's [Sidewalk Widths NYC](https://github.com/meliharvey/sidewalkwidths-nyc) project. Please visit their repository to learn more about the calculation.

| ![Point cloud](./media/examples/2386_9702_sw_obstacles.png) | ![Static objects](./media/examples/2386_9702_m3c2.png) |
|:---:|:---:|

<b>Example pointcloud.</b> Left: the point cloud with the sidewalk and points above it labeled. Right: static obstacles that remain after M3C2 change detection.<br/>

| ![Obstacle shapes](./media/examples/2386_9702_obst_shapes.png) | ![Segment categories](./media/examples/2386_9702_path_segments.png) | ![Obstacles-free width](./media/examples/2386_9702_ofw.png) |
|:---:|:---:|:---:|

<b>Path computation.</b> Left: obstacles converted to polygon shapes. Center: paths around obstacles categorised by accessibility. Right: final computed obstacle-free width.<br/>


---

## Folder Structure

 * [`datasets`](./datasets) _Demo dataset to get started_
   * [`ahn`](./datasets/ahn) _AHN elevation data_
   * [`bgt`](./datasets/bgt) _BGT topographical data_
   * [`pointcloud`](./datasets/pointcloud) _Example labeled urban point clouds_
 * [`media/examples`](./media/examples) _Visuals_
 * [`notebooks`](./notebooks) _Jupyter notebook tutorials_
 * [`src/upc_sw`](./src/upc_sw) _Python source code_

---

## Installation

1. Clone this repository:
    ```bash
    git clone https://github.com/Amsterdam-AI-Team/Urban_PointCloud_Sidewalk_Width.git
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Finally, install `cccorelib` and `pycc` by following the [instructions on their GitHub page](https://github.com/tmontaigu/CloudCompare-PythonPlugin/blob/master/docs/building.rst#building-as-independent-wheels). Please note, these two packages are not available on the Python Package Index (PyPi).

4. For [notebook 3](https://github.com/Amsterdam-AI-Team/Urban_PointCloud_Sidewalk_Width/blob/main/notebooks/3.%20Change%20detection%20M3C2.ipynb), we create a clean virtual environment and follow the instructions on the [CloudComPy](https://github.com/CloudCompare/CloudComPy) page to install this package. This, to avoid incompatibility issues when using the `CloudComPy` package and the `cccorelib` and `pycc` packages.

5. Check out the [notebooks](notebooks) for a demonstration.

---

## Usage

We provide tutorial [notebooks](notebooks) that demonstrate how the code can be used. Labeled example point clouds are provided to get started.

---

This repository was created by [Amsterdam Intelligence](https://amsterdamintelligence.com/) for the City of Amsterdam. See [our blog post](https://amsterdamintelligence.com/posts/computing-accessible-sidewalk-width-using-point-clouds-and-topographical-maps) on this topic for more details.
