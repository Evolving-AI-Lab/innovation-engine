//| This file is a part of the sferes2 framework.
//| Copyright 2009, ISIR / Universite Pierre et Marie Curie (UPMC)
//| Main contributor(s): Jean-Baptiste Mouret, mouret@isir.fr
//|
//| This software is a computer program whose purpose is to facilitate
//| experiments in evolutionary computation and evolutionary robotics.
//|
//| This software is governed by the CeCILL license under French law
//| and abiding by the rules of distribution of free software.  You
//| can use, modify and/ or redistribute the software under the terms
//| of the CeCILL license as circulated by CEA, CNRS and INRIA at the
//| following URL "http://www.cecill.info".
//|
//| As a counterpart to the access to the source code and rights to
//| copy, modify and redistribute granted by the license, users are
//| provided only with a limited warranty and the software's author,
//| the holder of the economic rights, and the successive licensors
//| have only limited liability.
//|
//| In this respect, the user's attention is drawn to the risks
//| associated with loading, using, modifying and/or developing or
//| reproducing the software by the user in light of its specific
//| status of free software, that may mean that it is complicated to
//| manipulate, and that also therefore means that it is reserved for
//| developers and experienced professionals having in-depth computer
//| knowledge. Users are therefore encouraged to load and test the
//| software's suitability as regards their requirements in conditions
//| enabling the security of their systems and/or data to be ensured
//| and, more generally, to use and operate it in the same conditions
//| as regards security.
//|
//| The fact that you are presently reading this means that you have
//| had knowledge of the CeCILL license and that you accept its terms.

#ifndef ONE_GENERATION_HPP_
#define ONE_GENERATION_HPP_

#include <algorithm>
#include <limits>

#include <boost/foreach.hpp>
#include <boost/multi_array.hpp>
#include <boost/array.hpp>
#include <boost/fusion/algorithm/iteration/for_each.hpp>
#include <boost/fusion/include/for_each.hpp>

#include <sferes/stc.hpp>
#include <exp/images/ea/ea_custom.hpp>
#include <sferes/fit/fitness.hpp>

#include <exp/images/continue_run/continue_run.hpp>

namespace sferes
{
	namespace ea
	{
		// Main class
		SFERES_EA(OneGeneration, EaCustom){
public:

	typedef boost::shared_ptr<Phen> indiv_t;

	typedef std::vector<indiv_t> pop_t;
	typedef typename pop_t::iterator it_t;
	typedef typename std::vector<std::vector<indiv_t> > front_t;
	typedef boost::array<float, 2> point_t;
	typedef boost::shared_ptr<Phen> phen_t;
	typedef boost::multi_array<phen_t, 2> array_t;
//	typedef boost::shared_ptr<Stat> stat_t;

	static const size_t res_x = Params::ea::res_x;
	static const size_t res_y = Params::ea::res_y;

	typedef Stat stat_t;

	OneGeneration() :
	_array(boost::extents[res_x][res_y]),
	_array_parents(boost::extents[res_x][res_y]),
	_jumps(0)
	{
	}

	void random_pop()
	{
		// parallel::init(); We are not using TBB

		// Original Map-Elites code
		// Intialize a random population
		this->_pop.resize(Params::pop::init_size);
		BOOST_FOREACH(boost::shared_ptr<Phen>&indiv, this->_pop)
		{
			indiv = boost::shared_ptr<Phen>(new Phen());
			indiv->random();
		}

		// Evaluate the initialized population
		this->_eval.eval(this->_pop, 0, this->_pop.size());

		// Add to archive for later printing
		int i = 0;
		BOOST_FOREACH(boost::shared_ptr<Phen>&indiv, this->_pop)
		{
			_add_to_archive(i, indiv, indiv);
			i++;
		}

//		std::cout << "Stopped at generation #0 before any selection" << std::endl;
//		exit(0);
	}

	//ADDED
	void setGen(size_t gen)
	{
		this->_gen = gen;
	}
	//ADDED END

	void epoch()
	{
	}

	const array_t& archive() const
	{	return _array;}
	const array_t& parents() const
	{	return _array_parents;}

	const unsigned long jumps() const
	{	return _jumps;}

protected:
	array_t _array;
	array_t _prev_array;
	array_t _array_parents;
	unsigned long _jumps;

	bool _add_to_archive(const int index, indiv_t i1, indiv_t parent)
	{
		bool added = false;	// Flag raised when the individual is added to the archive in any cell

		// We have a map of 1x1000 for the total of 1000 categories
		assert(1 == res_x);

		// Add to archive
		_array[0][index] = i1;
		_array_parents[0][index] = parent;

		return added;
	}

};
}
}
#endif

