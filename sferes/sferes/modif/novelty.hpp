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

#ifndef MODIFIER_NOVELTY_HPP
#define MODIFIER_NOVELTY_HPP

#include <Eigen/Core>
#include "sferes/parallel.hpp"
#include <boost/uuid/uuid.hpp>            // uuid class

//#include <boost/accumulators/accumulators.hpp>
//#include <boost/accumulators/statistics/stats.hpp>
//
//// Headers specifics to the computations we need
//#include <boost/accumulators/statistics/max.hpp>
//#include <boost/accumulators/statistics/min.hpp>

namespace sferes {
  namespace modif {
    namespace novelty {

      // compute the matrix of distances
      template<typename Phen>
      struct _distance_f {
        typedef std::vector<boost::shared_ptr<Phen> > pop_t;
        const pop_t& _pop;
        const pop_t& _archive;
        Eigen::MatrixXf& distances;

        ~_distance_f() { }
        _distance_f(const pop_t& pop, const pop_t& archive, Eigen::MatrixXf& d) :
          _pop(pop), _archive(archive), distances(d) {}
        _distance_f(const _distance_f& ev) :
          _pop(ev._pop), _archive(ev._archive), distances(ev.distances) {}

        void operator() (const parallel::range_t& r) const {
          for (size_t i = r.begin(); i != r.end(); ++i) {
            for (size_t j = 0; j < _archive.size(); ++j)
            {
            	float d = 0;

            	// Check if they are not the same image
            	if ((_pop[i] != _archive[j]) && (_pop[i]->id() != _archive[j]->id()))
            	{
#ifdef EUCLIDEAN_DISTANCE
            		// Euclidean distance
            		d = _pop[i]->dist(*_archive[j]);

            		#else
            		// Regular distance
            		d = _pop[i]->fit().dist(*_archive[j]);
#endif
            	}

              distances(i, j) = d;
            }
          }
        }
      };
    }

    // The novelty score will be stored in the last objective 'slot'
    // If there is only one objective (this->objs().size() == 1), then
    // this modifiers is a standard Novelty search algorithm [1]
    // otherwise, it is a "novelty-based multi-objectivization" [2]
    // See [2] for more explanations of the differences between
    // novelty search, multi-objective novelty search, and behavioral diversity
    //
    // * References
    // [1] Lehman, Joel, and Kenneth O. Stanley. "Abandoning objectives:
    // Evolution through the search for novelty alone."
    // Evolutionary computation 19.2 (2011): 189-223.
    //
    // [2] Mouret, Jean-Baptiste. "Novelty-based multiobjectivization."
    // New Horizons in Evolutionary Robotics. Springer Berlin Heidelberg,
    // 2011. 139-154.
    template<typename Phen, typename Params, typename Exact = stc::Itself>
    class Novelty {
     public:
      typedef boost::shared_ptr<Phen> phen_t;
      typedef std::vector<phen_t> pop_t;
      Novelty() : _rho_min(Params::novelty::rho_min_init), _not_added(0) {}

      template<typename Ea>
      void apply(Ea& ea)
      {
//      	boost::accumulators::accumulator_set<double, boost::accumulators::stats<boost::accumulators::tag::max> > acc_max;
//      	boost::accumulators::accumulator_set<double, boost::accumulators::stats<boost::accumulators::tag::min> > acc_min;

        SFERES_CONST size_t k = Params::novelty::k;
        // merge the population and the archive in a single archive
        pop_t archive = _archive;
        archive.insert(archive.end(), ea.pop().begin(), ea.pop().end());

        // we compute all the distances from pop(i) to archive(j) and store them
        Eigen::MatrixXf distances(ea.pop().size(), archive.size());
        novelty::_distance_f<Phen> f(ea.pop(), archive, distances);
        parallel::init();
        parallel::p_for(parallel::range_t(0, ea.pop().size()), f);

        // compute the sparseness of each individual of the population
        // and potentially add to the archive
        int added = 0;

        for (size_t i = 0; i < ea.pop().size(); ++i) {
          size_t nb_objs = ea.pop()[i]->fit().objs().size();
          Eigen::VectorXf vd = distances.row(i);

          // Get the k-nearest neighbors
          double n = 0.0;
          std::partial_sort(vd.data(),
                            vd.data() + k,
                            vd.data() + vd.size());

          // Sum up the total of distances from k-nearest neighbors
          // This is the novelty score
          n = vd.head<k>().sum() / k;

          // Set the novelty score to the last objective in the array of objectives
          ea.pop()[i]->fit().set_obj(nb_objs - 1, n);

//          std::cout << "rho = " << _rho_min << "; n = " << n << "\n";
//          acc_max(n);
//          acc_min(n);

          // Check if this individual is already in the archive
          if (!in_archive_already(ea.pop()[i]->id()) &&
          		(n > _rho_min			// Check if the novelty score passes the threshold
              || misc::rand<float>() < Params::novelty::add_to_archive_prob))
          {
          	// Add this individual to the permanent archive
          	_archive.push_back(ea.pop()[i]);

          	// Print this indiv just added
//            std::cout << "----> n = " << n << "; label = " << ea.pop()[i]->fit().label() << "; score = " << ea.pop()[i]->fit().score() << "; id = " << ea.pop()[i]->id()  <<"\n";
//          	std::cout << "----> n = " << n << "; label = " << "; id = " << ea.pop()[i]->id()  <<"\n";

            _not_added = 0;
            ++added;
          } else {
          	// Do not add this individual to the archive
            ++_not_added;
          }
        } // end for all individuals

        // update rho_min
        if (_not_added > Params::novelty::stalled_tresh)//2500
        {
          _rho_min *= 0.95;	// Lower rho_min
          _not_added = 0;		// After lowering the stalled threshold, we need to reset the _not_added count
        }
        if (_archive.size() > Params::novelty::k && added > Params::novelty::adding_tresh)//4
        {
          _rho_min *= 1.05f;	// Increase rho_min
        }

        std::cout<<"a size:"<<_archive.size()<<std::endl;

        // DEBUG
//        std::cout << "a size:"<<_archive.size()
//        		<< "; max: " << boost::accumulators::max(acc_max)
//        		<< "; min: " << boost::accumulators::min(acc_min)
//        		<< std::endl;

      }

      /*
			 * Check if this individual is already in the archive.
			 */
			const bool in_archive_already ( const boost::uuids::uuid& id )
			{
				/* Comment out to save computation time
				for (int i = 0; i < _archive.size(); ++i)
				{
					// Check if this id is found in the archive.
					if (_archive[i]->id() == id)
					{
						return true;
					}

				}
				*/

				return false;
			}

      /*
       * Getter of archive.
       *
       * This function is created for statistics class to save the archive down to gen file.
       * 2015-01-21
       */
      const pop_t& archive() const
      {
      	return _archive;
      }

      /*
       * Setter of archive.
       *
       * This function is created for statistics class to save the archive down to gen file.
       * 2015-01-21
       */
      void set_archive(const pop_t& archive)
      {
      	_archive.clear();

      	// Assign items to archive
      	_archive.insert(_archive.end(), archive.begin(), archive.end());
      }

     protected:
      pop_t _archive;
      float _rho_min;
      size_t _not_added;
    };
  } // modif
} // sferes

#endif
