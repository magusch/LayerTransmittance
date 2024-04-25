# LayerTransmittance

An application for calculating the transmittance of a layer of a given thickness and plotting the graph.
You can choose the material of the layer from the list of materials or enter the refractive index manually.
Choose angle of incidence and wavelength of the light. 
Add several layers. 

Also in plasmon mode we can calculate condition for plasmon excitation.

## Installation

The easiest way to run the application is to use the docker image.

```docker-compose build```

```docker-compose up```

If you don't want to build everything we can use another version that use only plotly for ploting:

``` git checkout without_matplotlib```

## Usage

• go to `http://localhost:8081/` in your browser
• enter the parameters of the multilayer structure (thickness, material, angle of incidence, wavelength)
• click "Run" button


