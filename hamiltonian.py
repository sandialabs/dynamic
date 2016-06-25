#/------------------------------------------------------------------------------
#|
#|      File name:      dynamic/hamiltonian.py      [Python module source code]
#|
#|      Synopsis:
#|      ---------
#|
#|          This module provides various classes related to a
#|          Hamiltonian formulation of mechanics.
#|
#|          The main class is Hamiltonian, and its instances
#|          are conceived as lists of HamiltonianTerms, which
#|          may individually involve one or more Variables.
#|          The Hamiltonian can give us its partial derivative
#|          with respect to any of these Variables.
#|
#|          Typically, we build up a Hamiltonian describing
#|          a complex system's dynamics by adding terms to it
#|          one at a time, as needed.
#|
#|          The most important class is PotentialEnergyTerm,
#|          which defines a class of potential energy function
#|          that depends on a set of generalized coordinates
#|          (their generalized positions, but not their
#|          velocities).  The partial derivatives of the
#|          potential with respect to the position variables
#|          can be retrieved in order to extract force
#|          components, which (together with those for other
#|          potential energy terms in which a given coordinate
#|          appears) are used to update velocity variables.
#|
#|          Additional classes will be defined as needed.
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

from typing import Callable,Iterable,Iterator,Set

import logmaster

from fixed                      import Fixed
from partialEvalFunc            import PartiallyEvaluatableFunction
from differentiableFunction     import BaseDifferentiableFunction
from dynamicFunction            import BaseDynamicFunction,SummerDynamicFunction
from dynamicVariable            import DynamicVariable,DerivedDynamicFunction,DifferentiableDynamicFunction

logger = logmaster.getLogger(logmaster.sysName + '.simulator')
    # The hamiltonian module is part of our core simulation component.

# A HamiltonianTerm is a primitive dynamic function (not expressed as
# a sum of other functions) giving a Hamiltonian energy as a function
# of some set of variables.  It should be differentiable with respect
# to all variables.  At the moment it has no features that a general
# DifferentiableDynamicFunction does not have, although implicitly it
# is built from a set of DynamicVariables whose time-derivatives are
# derived from the partial derivative of the Hamiltonian we are a part
# of with respect to the conjugate momentum variables.

class HamiltonianTerm(DifferentiableDynamicFunction): pass


# For our purposes, a Hamiltonian is most straightforwardly conceived
# as a list of terms, each of which is a function of some variables.
# For convenience, we also have the ability to quickly look up, for
# a variable, what are the terms in the Hamiltonian that include that
# variable.  Also, for each term we should be easily able to obtain
# its partial derivative with respect to any variable.

    # Forward declaration for use by embedded class definitions.
class Hamiltonian(DifferentiableDynamicFunction): pass

class Hamiltonian(DifferentiableDynamicFunction):

    # Private data members:
    #
    #   inst._terms:Set[HamiltonianTerms] - The set of Hamiltonian terms making up this
    #       Hamiltonian.
    #
    #   inst._varTerms:Set[HamiltonianTerm] - Maps variables to the set of terms of
    #       this Hamiltonian that mention them.
    #
    #   inst._summer:SummerDynamicFunction - A dynamic function that just adds our
    #       terms together; this is used to evaluate the Hamiltonian.
    #
    #   inst._partials:Dict[DerivedDynamicFunction] - These dynamic functions are the
    #       partial derivatives of this Hamiltonian with respect to its variables.
    #       This is a cache which is incrementally computed.  This differs from
    #       the attribute of the same name in DifferentiableDynamicFunction in
    #       that its key is the DynamicVariable object, not its index.  This is
    #       useful since our set of variables may change over time.

    # The initializer for a Hamiltonian differs from the initializer for
    # a generic DifferentiableDynamicFunction in that, instead of providing
    # the list of variables and the underlying differentiable function up
    # front, we will build them up incrementally as terms are added to this
    # Hamiltonian.  This allows the Hamiltonian for a given network to be
    # adjusted dynamically as the network structure is built and modified.

    def __init__(inst):

            # Do default initialization for DifferentiableDynamicFunction instances.
        DifferentiableDynamicFunction.__init__(inst)   

        inst._setTerms()                            # Set our set of terms (initially to an empty set).
        inst._function = inst.hamFunction           # Our function to evaluate Hamiltonians.
        inst._summer = SummerDynamicFunction(inst)  # Does the job of summing our terms.
        
    def hamFunction(inst, *args):
        
        # Note: No explicit arguments here!  We ignore any arguments
        # we receive and just look at our variables instead.  This 
        # works by just calling our summer.

        inst._summer()

    # This public embedded class generates an Iterable for a given Hamiltonian
    # which provides an Iterator that can be used to iterate through our terms.

    class TermsIterable(Iterable[BaseDynamicFunction]):
        def __init__(inst, ham:Hamiltonian):
            inst._hamiltonian = ham
        def __iter__(inst):
            return iter(ham._terms)

    def __iter__(inst):
        return TermsIterable(inst)

    # Set the set of terms of this Hamiltonian to the given set.  Please note
    # that doing this entirely replaces the existing set of terms (if any).

    def _setTerms(inst, terms:Set[HamiltonianTerm]=set()):    # Empty list by default.

        inst._terms = set()         # Initially empty set of terms.
        inst._varTerms = dict()     # Initially empty map from variables to sets of terms.
        inst._partials = dict()     # Initially empty map from variables to their partials.

        for term in terms:
            inst.addTerm(term)

    # This public embedded class generates an Iterator that can be used to
    # iterate through the partial derivatives of a Hamiltonian's terms with
    # respect to the given DynamicVariable.

    class TermsPartialDerivIterator(Iterator[BaseDynamicFunction]):
        def __init__(inst, termIter:Iterable[HamiltonianTerm], var:DynamicVariable):
            inst._termIter = iter(termIter)
            inst._variable = var
        def __iter__(inst): return inst
        def __next__(inst):
            term = next(inst._termIter)
            return term.dynPartialDerivWRT(inst._variable)
        
    # This public embedded class generates an Iterable for a given Hamiltonian
    # and DynamicVariable included in that Hamiltonian which provides an Iterator
    # that can be used to iterate through the partial derivatives of our terms
    # with respect to the given DynamicVariable.  Automatically skips terms which
    # would be zero because they don't even contain the given variables.

    class TermsPartialDerivIterable(Iterable[BaseDynamicFunction]):
        def __init__(inst, ham:Hamiltonian, var:DynamicVariable):
            inst._termList = ham.termsContaining(v)
            inst._variable = var
        def __iter__(inst):
            return TermsPartialDerivIterator(inst._termList, inst._variable)


    # Public member functions:
    #
    #   .addTerm(term:HamiltonianTerm) - Merges the given term to this
    #       Hamiltonian.  Merges its variable list into ours.

    def addTerm(inst, term:HamiltonianTerm):

        logger.debug("Adding term %s to Hamiltonian %s..." %
                     (str(term), str(inst)))

        if term not in inst._terms:

            logger.debug("This is a new term, really adding it...")
            
            inst._terms |= {term}

                # Merge the variable list for the new term into that
                # for the overall Hamiltonian.

            inst._varList = list(set(inst._varList) | set(term._varList))

                # For each of the new term's variables, remember that
                # this term is in the set of terms that references
                # that variable.  Also, if some of the variables are
                # actually dynamic functions depending on yet other
                # variables, then remember that this term is in the
                # set of terms that references those other variables.

            for var in term._varList:

                inst._register(var, term)


        # Remember that the given variable influences the given Hamiltonian term.
        # This updates data structures mapping variables to the set of terms that
        # they influence.  As a side-effect, we forget the partial derivative of
        # this Hamiltonian with respect to that variable since it may need to be
        # recomputed.  For the case of "variables" that are actually derived
        # dynamic functions, we also recursively register the variables that they
        # depend on as also influencing the value of the given Hamiltonian term.

    def _register(inst, var:BaseDynamicFunction, term:HamiltonianTerm):

        logger.debug("Registering that variable %s influences term %s..." %
                     (str(var), str(term)))

            # If we're already aware that this variable is associated
            # with some set of terms that it influences, make note of
            # that; otherwise, we're not yet aware that it influences
            # any terms.

        if term in inst._varTerms:
                # Get the set of terms already associated w. this variable.
            varTerms = set(inst._varTerms[var]) 
        else:
            varTerms = set()    # Empty set of terms already associated with that variable.

            # Add the given term into the set of terms that we're aware
            # that this variable influences, and remember that for
            # future reference.

        newVarTerms = varTerms | {term}     # Union the new term into the variable's set.

            # If this knowledge is new (that this variable is influencing
            # the value of this term), then the partial derivative of the
            # Hamiltonian with respect to this variable probably needs to
            # be recomputed, so clear our cache of that partial derivative.

        if len(newVarTerms) > len(varTerms):    # Size of set grew?

            inst._varTerms[var] = newVarTerms   # Store new set back in the dict.

            if var in inst._partials:
                del inst._partials[var]      # Clear any cached partial derivative info.

            # If this "variable" is in fact a derived dynamic function,
            # then go into *its* variables and register them as influencing
            # the value of this term as well.  (Eventually, this recursive
            # process should bottom out with some real dynamic variables.)

        if isinstance(var, DerivedDynamicFunction):
            moreVars = var.varList
            for underlyingVar in moreVars:
                inst._register(underlyingVar, term)
            
    # This implementation of the inst.dynPartialDerivWRT() method overrides
    # the one defined in our parent class DifferentiableDynamicFunction.  We
    # need to do this because our partial derivative is inferred from a set
    # of Hamiltonian terms, rather than directly from an underlying (non-
    # dynamic) base differentiable function.
    #
    #   .dynPartialDerivWRT(v:DynamicVariable) - Given the identification
    #       of a particular dynamic variable mentioned in this Hamiltonian,
    #       return a DerivedDynamicFunction object which is a callable
    #       function that, given a point in time t, evaluates
    #       the partial derivative of the Hamiltonian with respect to that
    #       variable at that point in time (given the values that other
    #       variables would have at that point in time).
    #
    #       To implement this efficiently, we use a map to keep track of the
    #       list of terms that mention a given variable.
    #   
    #   .termsContaining(v:DynamicVariable) - Returns a list of all the
    #       terms within this Hamiltonian that involve the given variable.
    #
    
    def dynpartialDerivWRT(self, v:DynamicVariable) -> DerivedDynamicFunction:

        # If this Hamiltonian's partial derivative with respect to the
        # given variable has already been generated, don't bother generating
        # it again; just return the already-cached object.

        if v in self._partials:
            return self._partials[v]

        # OK, our partial derivative with respect to the given variable
        # hasn't yet been generated, at least not since the set of terms
        # involving that variable was changed.
        # First, generate an iterable that can be used to iterate through
        # the dynamic partial derivatives of our terms with respect to
        # the given variable.  It skips terms not including the variable.

        dynPartialDerivIterable = TermsPartialDerivIterable(self, v)

        # Now we generate a SummerDynamicFunction object which will sum
        # over those partial derivative terms.

        dynPartialsSummmer = SummerDynamicFunction(dynPartialDerivIterable)

        # Cache the result so we don't have to keep regenerating it.

        self._partials[v] = dynPartialsSummer

        # Return it.

        return dynPartialsSummer
    

    def termsContaining(self, v:DynamicVariable):

        if self._varTerms.has_key(v):
            return self._varTerms[v]
        else:
            return []
