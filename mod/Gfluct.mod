TITLE Fluctuating conductances

COMMENT
-----------------------------------------------------------------------------

	Fluctuating conductance model for synaptic bombardment
	======================================================

THEORY

  Synaptic bombardment is represented by a stochastic model containing
  two fluctuating conductances g_e(t) and g_i(t) descibed by:

     Isyn = g_e(t) * [V - E_e] + g_i(t) * [V - E_i]
     d g_e / dt = -(g_e - g_e0) / tau_e + sqrt(D_e) * Ft
     d g_i / dt = -(g_i - g_i0) / tau_i + sqrt(D_i) * Ft

  where E_e, E_i are the reversal potentials, g_e0, g_i0 are the average
  conductances, tau_e, tau_i are time constants, D_e, D_i are noise diffusion
  coefficients and Ft is a gaussian white noise of unit standard deviation.

  g_e and g_i are described by an Ornstein-Uhlenbeck (OU) stochastic process
  where tau_e and tau_i represent the "correlation" (if tau_e and tau_i are 
  zero, g_e and g_i are white noise).  The estimation of OU parameters can
  be made from the power spectrum:

     S(w) =  2 * D * tau^2 / (1 + w^2 * tau^2)

  and the diffusion coeffient D is estimated from the variance:

     D = 2 * sigma^2 / tau


NUMERICAL RESOLUTION

  The numerical scheme for integration of OU processes takes advantage 
  of the fact that these processes are gaussian, which led to an exact
  update rule independent of the time step dt (see Gillespie DT, Am J Phys 
  64: 225, 1996):

     x(t+dt) = x(t) * exp(-dt/tau) + A * N(0,1)

  where A = sqrt( D*tau/2 * (1-exp(-2*dt/tau)) ) and N(0,1) is a normal
  random number (avg=0, sigma=1)


IMPLEMENTATION

  This mechanism is implemented as a nonspecific current defined as a
  point process.


PARAMETERS

  The mechanism takes the following parameters:

     E_e = 0  (mV)		: reversal potential of excitatory conductance
     E_i = -75 (mV)		: reversal potential of inhibitory conductance

     g_e0 = 0.0121 (umho)	: average excitatory conductance
     g_i0 = 0.0573 (umho)	: average inhibitory conductance

     std_e = 0.0030 (umho)	: standard dev of excitatory conductance
     std_i = 0.0066 (umho)	: standard dev of inhibitory conductance

     tau_e = 2.728 (ms)		: time constant of excitatory conductance
     tau_i = 10.49 (ms)		: time constant of inhibitory conductance


Gfluct2: conductance cannot be negative


REFERENCE

  Destexhe, A., Rudolph, M., Fellous, J-M. and Sejnowski, T.J.  
  Fluctuating synaptic conductances recreate in-vivo--like activity in
  neocortical neurons. Neuroscience 107: 13-24 (2001).

  (electronic copy available at http://cns.iaf.cnrs-gif.fr)


  A. Destexhe, 1999

-----------------------------------------------------------------------------
ENDCOMMENT


COMMENT
-----------------------------------------------------------------------------
Modified Gfluct2:
- Added `delay` parameter to allow fluctuations to start later
- Added `inhib` flag to optionally disable inhibitory fluctuations

-----------------------------------------------------------------------------
ENDCOMMENT

INDEPENDENT {t FROM 0 TO 1 WITH 1 (ms)}

NEURON {
	POINT_PROCESS Gfluct2
	RANGE g_e, g_i, E_e, E_i, g_e0, g_i0, g_e1, g_i1
	RANGE std_e, std_i, tau_e, tau_i, D_e, D_i
	RANGE new_seed
	RANGE delay, inhib
	NONSPECIFIC_CURRENT i
}

UNITS {
	(nA) = (nanoamp)
	(mV) = (millivolt)
	(umho) = (micromho)
}

PARAMETER {
	dt		(ms)
	delay = 0 (ms)          : delay before fluctuations start
	inhib = 1               : 1 = include inhibition, 0 = no inhibition

	E_e	= 0 	(mV)
	E_i	= -75 	(mV)

	g_e0	= 0.0121 (umho)
	g_i0	= 0.0573 (umho)

	std_e	= 0.0030 (umho)
	std_i	= 0.0066 (umho)

	tau_e	= 2.728	(ms)
	tau_i	= 10.49	(ms)
}

ASSIGNED {
	v	(mV)
	i 	(nA)
	g_e	(umho)
	g_i	(umho)
	g_e1	(umho)
	g_i1	(umho)
	D_e	(umho umho /ms)
	D_i	(umho umho /ms)
	exp_e
	exp_i
	amp_e	(umho)
	amp_i	(umho)
}

INITIAL {
	g_e1 = 0
	g_i1 = 0
	if(tau_e != 0) {
		D_e = 2 * std_e * std_e / tau_e
		exp_e = exp(-dt/tau_e)
		amp_e = std_e * sqrt( (1-exp(-2*dt/tau_e)) )
	}
	if(tau_i != 0) {
		D_i = 2 * std_i * std_i / tau_i
		exp_i = exp(-dt/tau_i)
		amp_i = std_i * sqrt( (1-exp(-2*dt/tau_i)) )
	}
}

BREAKPOINT {
	SOLVE oup

	if (t < delay) {
		g_e = 0
		g_i = 0
		i = 0
	} else {
		g_e = g_e0 + g_e1
		if(g_e < 0) { g_e = 0 }

		if (inhib == 1) {
			g_i = g_i0 + g_i1
			if(g_i < 0) { g_i = 0 }
		} else {
			g_i = 0
		}

		i = g_e * (v - E_e) + g_i * (v - E_i)
	}
}

PROCEDURE oup() {
	if (t >= delay) {
		if(tau_e!=0) {
			g_e1 = exp_e * g_e1 + amp_e * normrand(0,1)
		}
		if(inhib == 1 && tau_i!=0) {
			g_i1 = exp_i * g_i1 + amp_i * normrand(0,1)
		}
	}
}

PROCEDURE new_seed(seed) {
	set_seed(seed)
	VERBATIM
	  printf("Setting random generator with seed = %g\n", _lseed);
	ENDVERBATIM
}
