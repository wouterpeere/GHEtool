import pygfunction as gt

from GHEtool.VariableClasses.PipeData.SingleUTube import SingleUTube
from GHEtool.VariableClasses.FluidData import FluidData


class Separatus(SingleUTube):
    """
    This class contains the model for the Separatus probe. Separatus is a new player in the geothermal space and
    uses a unique 'splitpipe'-technology. This technology inserts a membrane in the middel of a pipe with DN50, so that
    the inlet and outlet flows are separated.

    The model in this class has been obtained in close collaboration between Separatus AG (Swiss) and Enead BV (Belgium)
    based on real-life measurements from projects. It was found that the Separatus probe can be modelled like
    a single U-tube with a specific set of design parameters and an extra contact resistance.

    The implemented model is the first step towards designing a system with the Separatus technology. In the future, this
    model will be updated when new research has been conducted.

    More information on this technology and its advantages can be found here: https://separatus.ch/en.
    """

    def __init__(self, k_g: float = None):
        """
        
        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/mK]
        """
        super().__init__(k_g=k_g,
                         r_in=(35.74 / 2 - 3) * 0.001,
                         r_out=(35.74 / 2) * 0.001,
                         k_p=0.44,
                         D_s=36 / 2 * 0.001)

    def pipe_model(self, fluid_data: FluidData, k_s: float, borehole: gt.boreholes.Borehole) -> gt.pipes._BasePipe:
        """
        This function returns the pipe model for the Separatus probe.
        A Separatus heat exchanger can be modelled by using the model of a single U tube, with an extra contact resistance
        of 0.03 W/(mK) to account for the intermediate wall inside the probe. This value of 0.03W/(mK) was obtained by
        the company based on real-life measurements.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data
        k_s : float
            Ground thermal conductivity
        borehole : Borehole
            Borehole object

        Returns
        -------
        BasePipe
        """
        single_u: gt.pipes._BasePipe = super().pipe_model(fluid_data, k_s, borehole)

        # add 0.03 W/(mK) as a contact resistance
        single_u.R_fp += 0.03

        return single_u

    def __repr__(self):
        return 'Separatus heat exchanger'
