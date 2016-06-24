#/==============================================================================
#|                          TOP OF FILE:    coordinate.py
#/------------------------------------------------------------------------------
#|
#|      File name:      dynamic/coordinate.py
#|
#|      File type:                                  [Python module source code]
#|
#|      Description:
#|      ------------
#|
#|          This module provides a class Coordinate whose instances
#|          are objects representing generalized-coordinate variables
#|          within the context of a dynamical system.
#|
#|          Each Coordinate object maintains various contextual
#|          information, such as which other coordinates it interacts
#|          with (and via what terms in the system's Hamiltonian),
#|          and what time step it is currently at in the simulation
#|          (for both its position and associated momentum variables),
#|          what its generalized mass is and its associated kinetic
#|          energy function, and what are the current values of
#|          its position and associated velocity variables).
#|
#|          The values of position and velocity variables are updated
#|          as needed using an invertible centered-difference update
#|          rule operating in fixed-point arithmetic.  This allows the
#|          simulation to be exactly reversed and repeated as many
#|          times as necessary, with no losses.
#|
#|          Coordinates support operations such as advancing (or
#|          retracting) their state to any later (or earlier) point in
#|          time as requested.  Messages are automatically sent to
#|          neighboring coordinates to cause them to also update their
#|          states as needed.  In general, only a "light cone" space-
#|          time volume's worth of updates needs to be performed in
#|          order to calculate a coordinate value at any point in time.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from abc import ABCMeta,abstractmethod      # Abstract base class support.

from fixed  import Fixed     # Fixed-precision math class.
from typing import Callable

from dynamicVariable        import DynamicVariable,DerivedDynamicFunction
from hamiltonian            import HamiltonianTerm,Hamiltonian
from kineticEnergyFunction  import SimpleQuadraticKineticEnergyFunction

# Base class for a dynamic variable appearing in a Hamiltonian.  Such variables
# remember the Hamiltonian that they are associated with and their time derivative
# can be inferred from it.  If their Hamiltonian is changed, then their time
# derivative needs to be recomputed; the setTimeDeriv() method does this.
#However, it is abstract and must be defined by subclasses.

class HamiltonianVariable(DynamicVariable,metaclass=ABCMeta):

    def __init__(inst, name:str=None, value:Fixed=Fixed(0), time:int=0,
                 hamiltonian:Hamiltonian=None):

        if hamiltonian != None:  inst.hamiltonian = hamiltonian
            # Goes ahead and sets our time derivative as a side-effect.

        DynamicVariable.__init__(inst, name, value, time)

    @property
    def hamiltonian(self):

        if hasattr(self,'_hamiltonian'):
            return self._hamiltonian
        else:
            return None

    @hamiltonian.setter
    def hamiltonian(self, hamiltonian:Hamiltonian):

        if hamiltonian != None:

            self._hamiltonian = hamiltonian
            self.setTimeDeriv()

    @abstractmethod
    def setTimeDeriv(self): pass

# Forward declarations to avoid circularity.

class PositionVariable(HamiltonianVariable): pass
class MomentumVariable(HamiltonianVariable): pass
#class VelocityVariable(Variable): pass

#  A (generalized) PositionVariable is a variable whose time
#  derivative is ∂H/∂p, where H is a Hamiltonian function, p is
#  the corresponding conjugate MomentumVariable, and ∂H/∂p
#  denotes the partial derivative of H with respect to p.

#  When we create a PositionVariable, we (optionally) specify
#  the MomentumVariable that it is associated with.

class PositionVariable(HamiltonianVariable):

    # Public properties:
    #
    #   .hamiltonian - The Hamiltonian energy function of the system
    #       that this position variable is a part of.  
    #
    #   .conjugateMomentum - The momentum variable that this position
    #       variable is associated with in canonical coordinates.
    #
    # Private data members:
    #
    #   ._hamiltonian - The Hamiltonian energy function of the system
    #       that this position variable is a part of.  Accessed through
    #       the .hamiltonian public @property.
    #
    #   ._conjugateMomentum  - The momentum variable that this position
    #       variable is associated with in canonical coordinates.
    #       Accessed through the .conjugateMomentum public @property.
    #

    def __init__(inst, name:str=None, value:Fixed=Fixed(0), time:int=0,
                 hamiltonian:Hamiltonian=None, conjugateMomentum:MomentumVariable=None):

        # Remember our conjugate momentum variable.

        inst.conjugateMomentum  = conjugateMomentum

        # Do default initialization for Hamiltonian variables.
        
        HamiltonianVariable.__init__(inst, name, value, time, hamiltonian)

        # If we know our Hamiltonian already, we can do ahead and set
        # up the dynamic function for our time derivative.

        if hamiltonian != None:
            inst.setTimeDeriv()
                                              
    @property
    def conjugateMomentum(self):
        
        if hasattr(self,'_conjugateMomentum'):
            return self._conjugateMomentum
        else:
            return None

    @conjugateMomentum.setter
    def conjugateMomentum(self, conjMom:MomentumVariable):

        # If the conjugate momentum variable is being provided,
        # and we're not already configured to use it, then use it.

        if conjMom != None and conjMom != self.conjugateMomentum:
        
            self._conjugateMomentum = conjMom
            self.setTimeDeriv()

            # Also inform our conjugate momentum variable that
            # we are its "conjugate position" variable.

            conjMom.conjugatePosition = self

    def setTimeDeriv(self):
        if hasattr(self, '_hamiltonian'):
                # Create the dynamic function representing our time derivative.
                # This is just the partial derivative of the Hamiltonian with
                # respect to our conjugate momentum variable, ∂q/∂t = ∂H/∂p.
            posTimeDeriv = self.hamiltonian.dynPartialDerivWRT(conjugateMomentum)
                # Store that thang for later reference.
            self._timeDeriv = posTimeDeriv

    
#  A (generalized) MomentumVariable is a variable whose time
#  derivative is -∂H/∂q, where H is a Hamiltonian function, q is
#  the corresponding conjugate PositionVariable, and ∂H/∂q denotes
#  the partial derivative of H with respect to q.

#  When we create a MomentumVariable, we (optionally) specify
#  the PositionVariable that it is associated with.

class MomentumVariable(HamiltonianVariable):

    # Private data members:
    #
    #   ._conjugatePosition  - The position variable that this position
    #       variable is associated with in canonical coordinates.
    #       Accessed through the .conjugatePosition @property.
    #
    # Public data members:
    #
    #   .hamiltonian - The Hamiltonian energy function of the system
    #       that this momentum variable is a part of.

    def __init__(inst, name:str=None, value:Fixed=Fixed(0), time:int=0,
                 hamiltonian:Hamiltonian=None,
                 conjugatePosition:PositionVariable=None):

        inst.conjugatePosition = conjugatePosition

            # Do default initialization for Hamiltonian variables.
        HamiltonianVariable.__init__(inst, name, value, time, hamiltonian)

    @property
    def conjugatePosition(self):
        if hasattr(self,'_conjugatePosition'):
            return self._conjugatePosition
        else:
            return None

    @conjugatePosition.setter
    def conjugatePosition(self, conjPos):

        # If the conjugate position variable is being provided,
        # and we're not already configured to use it, then use it.

        if conjPos != None and conjPos != self.conjugatePosition:
            
            self._conjugatePosition = conjPos
            self.setTimeDeriv()

            # Also inform our conjugate position variable that
            # we are its conjugate momentum variable.

            conjPos.conjugateMomentum = self

    def setTimeDeriv(self):
        if hasattr(self, '_hamiltonian'):
            
                # Create the dynamic function representing our time derivative.
                # This is just the negative of the partial derivative of the
                # Hamiltonian with respect to our conjugate position variable,
                # ∂p/∂t = -∂H/∂q.

            dH_over_dq = self.hamiltonian.dynPartialDerivWRT(conjugatePosition)
            momTimeDeriv = NegatorDynamicFunction(dH_over_dq)
            
                # Store that thang for later reference.

            inst._timeDeriv = momTimeDeriv            

        

#  A VelocityVariable is a variable v that is related to a
#  corresponding momentum variable p by the relation p=mv, where
#  m is an effective mass which is normally a constant.  Note
#  that this formulation does not encompass relativistic or
#  quantum-mechanical concepts of momentum.  Momentum and
#  velocity variables are normally closely locked together.

# Here, we implement a VelocityVariable v as a DerivedDynamicFunction that is
# derived from a corresponding MomentumVariable p.  Its value is defined
# by v=p/m where m is a corresponding effective generalized mass.

class VelocityVariable(DerivedDynamicFunction):

    def __init__(inst, momVar:MomentumVariable, mass=None):

        if mass == None:  mass = 1      # Default to unit mass.

        inst._momVar = momVar
        inst._mass = mass

        velFunc = lambda p: p/mass

        DerivedDynamicFunction.__init__(inst, [momVar], velFunc)

    @property
    def value(inst):
        return inst()

#  A CanonicalCoordinatePair object is essentially a pair of
#  a generalized position coordinate and its corresponding
#  conjugate momentum.
#
#  When these coordinate-pair objects are first created, by
#  default the positions are specified at time step 0, and the
#  momenta at time step 1, to allow leapfrogging.
#
#  As a naming convention, if the generalized position coordinate
#  is named 'x' then its conjugate momentum coordinate will be
#  named 'px'.

class CanonicalCoordinatePair:

    def __init__(inst, name:str=None, posval:Fixed=Fixed(0),
                 momval:Fixed=Fixed(0), postime:int=0, 
                 hamiltonian:Hamiltonian=None):

        inst.name = name

        if isinstance(name,str):
            pname = 'p' + name
        else:
            pname = None

        #-- Create the position and momentum variables.
            
        q = PositionVariable(name, hamiltonian=hamiltonian)
        p = MomentumVariable(pname, hamiltonian=hamiltonian)

        #-- Tie those two lil' guys together.  They'll
        #   respond by automatically setting up their time
        #   derivative functions if the Hamiltonian is set.
        
        q.conjugateMomentum = p

        #-- Set up initial position and momentum values.

        q.value = posval;   q.time = postime
        p.value = momval;   p.time = postime + 1

        #-- Remember these dynamic variables internally for future reference.

        inst._posVar = q
        inst._momVar = p

    @property
    def positionVariable(self):
        return self._posVar

    @property
    def momentumVariable(self):
        return self._momVar
        
    @property
    def hamiltonian(self):

        if hasattr(self,'_hamiltonian'):
            return self._hamiltonian
        else:
            return None

    @hamiltonian.setter
    def hamiltonian(self, hamiltonian:Hamiltonian):

        if hamiltonian != None:

            self._hamiltonian = hamiltonian

            # Tell both variables in this pair what their Hamiltonians are.

            self.q.hamiltonian = hamiltonian
            self.p.hamiltonian = hamiltonian


# ReinitializationException - The semantics of this class of
#   exceptions is that the program attempted to re-initialize
#   some structure that was previously initialized, and where
#   such reinitialization is not allowed.

class ReinitializationException(Exception): pass

# DynamicCoordinate class.  For our purposes here, a DynamicCoordinate
# always means a canonical coordinate pair (q,p), where q is a
# generalized position coordinate and p is its associated conjugate
# momentum coordinate.  Further, by default all coordinates come
# equipped with an associated kinetic-energy Hamiltonian term of the
# form (1/2)m*v^2 = (1/2)p^2/m, where m is an effective mass associated
# with the coordinate.  Please note that this is a simple nonrelativistic
# expression for the kinetic energy, and would need to be modified for
# other scenarios.  The partial wrt p of this term is just p/m=v, and so
# that becomes the d/dt for the position q.  Meanwhile, a Coordinate can
# be decorated with additional potential energy or interaction terms which
# depend upon the q of this (and possibly other) coordinates in the system;
# the partial wrt q of these terms will determine the force dp/dt that
# updates the momentum variable.

class DynamicCoordinate:

    # Public properties:
    #
    #       .mass [Real] - Effective mass value associated with
    #           this dynamic coordinate.
    #
    #       .hamiltonian [Hamiltonian] - The overall Hamiltonian
    #           for the system that this particular DynamicCoordinate
    #           is a part of.  This is a "set-once" property.
    #           (Subsequent attempts to set it after the first will
    #           generate an exception.)

    # Public data members:
    #
    #       name [str] - Name of this coordinate, as a string.  (For
    #           simple nodes, this will generally be the same as the
    #           node name.)
    #
    #       ccp [CanonicalCoordinatePair] - This object holds the
    #           coordinate's position and momentum degrees of freedom.
    #
    #       position [Fixed] - Generalized position of this coordinate
    #       velocity [Fixed] - Generalized velocity of this coordinate
    #
    #       .kinetic_term - A term in the system's Hamiltonian that
    #           depends only on the generalized velocity of this
    #           coordinate (and no other positions or velocities).
    #
    #       .potential_term - A term in the system's Hamiltonian that
    #           depends only on the generalized position of this
    #           coordinate (and no other positions or velocities).
    #
    #       .interaction_terms - A list of pairs (T,n), where T is an
    #           interaction term in the system's Hamiltonian whose
    #           value depends on the generalized positions of this
    #           and other coordinates.
    #
    #
    #       pos_t [Integral] - Time step index of cur. position coordinate.
    #       vel_t [Integral] - Time step index of cur. velocity coordinate.
    #
    # Private data members:
    #
    #       ._hamiltonian [Hamiltonian] - The overall Hamiltonian
    #           for the system that this particular DynamicCoordinate
    #           is a part of.
    #
    
    def __init__(inst, name:str=None, mass=None, hamiltonian:Hamiltonian=None):

            # Give a dynamical coordinate a unit mass by default.

        if mass==None: mass = 1

            # Remember how to get to our Hamiltonian.

        inst.hamiltonian = hamiltonian

            # Create our dynamical guts, namely a CanonicalCoordinatePair (q,p).
        
        inst.ccp = CanonicalCoordinatePair(name, hamiltonian=hamiltonian)

            # Next we need to create the kinetic energy term associated
            # with this dynamical coordinate, and add it to the Hamiltonian.
            # First we create a generic quadratic kinetic energy function.

        KEfunc = SimpleQuadraticKineticEnergyFunction(m=mass)

            # Generate the velocity "variable" (really, a derived function
            # of momentum) for this coordinate.

        v = VelocityVariable(inst.ccp._momVar, mass)
        inst._velVar = v

            # Put the velocity variable together with the kinetic energy
            # function to generate a new Hamiltonian term.

        KEHterm = HamiltonianTerm([v], KEfunc)
        

    @property
    def positionVariable(self):
        return self.ccp.positionVariable

    @property
    def momentumVariable(self):
        return self.ccp.momentumVariable
        
    @property
    def hamiltonian(self):

        if self.hasattr('_hamiltonian'):
            return self._hamiltonian
        else:
            return None

    @hamiltonian.setter
    def hamiltonian(self, hamiltonian:Hamiltonian):

        if hamiltonian != None:

            if self.hamiltonian != None:

                self._hamiltonian = hamiltonian
                
            else:

                raise ReinitializationException()



