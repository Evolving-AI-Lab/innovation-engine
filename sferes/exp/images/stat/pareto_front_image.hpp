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




#ifndef PARETO_FRONT_IMAGE_HPP_
#define PARETO_FRONT_IMAGE_HPP_

#include <boost/serialization/shared_ptr.hpp>
#include <boost/serialization/nvp.hpp>


#include <boost/fusion/include/sequence.hpp>
#include <boost/fusion/include/make_vector.hpp>
#include <boost/fusion/include/next.hpp>


#include <sferes/stc.hpp>
#include <sferes/parallel.hpp>
#include <sferes/fit/fitness.hpp>
#include <sferes/stat/stat.hpp>

#include <sferes/ea/crowd.hpp>
#include "image_stat.hpp"		// ImageStat

namespace sferes {
  namespace stat {
    SFERES_STAT(ParetoFrontImage, ImageStat) {
    public:
      typedef std::vector<boost::shared_ptr<Phen> > pareto_t;
      typedef std::vector<boost::shared_ptr<Phen> > raw_pop_t;

      // asume a ea.pareto_front() method
      template<typename E>
      void refresh(const E& ea)
      {
      	// Save the pop and archive
      	_pop = ea.pop();
      	_archive = boost::fusion::at_c<Params::cont::getPopIndex>(ea.fit_modifier()).archive();

      	// Record pareto front
      	// No use of pareto for now
      	/*
        _pareto_front = ea.pareto_front();
        parallel::sort(_pareto_front.begin(), _pareto_front.end(),
                       fit::compare_objs_lex());
        this->_create_log_file(ea, "pareto.dat");

        if (ea.dump_enabled())
        {
          show_all(*(this->_log_file), ea.gen());
          //this->_log_file->close();
        }
        */

				// Create the directory
      	int gen = ea.gen();

      	if (gen % Params::image::image_dump_period == 0)
      	{
					const std::string gen_dir = this->_make_gen_dir(ea.res_dir(), gen);
					std::string image_gen = boost::lexical_cast<std::string>(ea.gen());		// generation

					for (size_t i = 0; i < _archive.size(); ++i)
					{
						// Print out images from the archive at the last generation
						std::string label = boost::lexical_cast<std::string>(_archive[i]->fit().label());
						std::string score = boost::lexical_cast<std::string>(_archive[i]->fit().score());
						std::string image_file = gen_dir + "/ar_" + boost::lexical_cast<std::string>(i) + "_" + label + "_" + score;

	//					std::cout << "A --- " << _archive[i]->fit().obj(0) << " ---" << label << " --- " << score << "\n";

						_archive[i]->log_best_image_fitness(image_file);
				}
      	}

        // Print the current progress
        this->printProgress(ea.gen());
      }

      void show(std::ostream& os, size_t k) const {
        os<<"log format : gen id obj_1 ... obj_n"<<std::endl;
        show_all(os, 0);
        _pareto_front[k]->develop();
        _pareto_front[k]->show(os);
        _pareto_front[k]->fit().set_mode(fit::mode::view);
        _pareto_front[k]->fit().eval(*_pareto_front[k]);
        os << "=> displaying individual " << k << std::endl;
        os << "fit:";
        for (size_t i =0; i < _pareto_front[k]->fit().objs().size(); ++i)
          os << _pareto_front[k]->fit().obj(i) << " ";
        os << std::endl;
        assert(k < _pareto_front.size());
      }
      const pareto_t& pareto_front() const {
        return _pareto_front;
      }

      template<class Archive>
      void serialize(Archive & ar, const unsigned int version) {
        ar & BOOST_SERIALIZATION_NVP(_pareto_front);
        ar & BOOST_SERIALIZATION_NVP(_pop);
        ar & BOOST_SERIALIZATION_NVP(_archive);
      }

      void show_all(std::ostream& os, size_t gen = 0) const
      {
        for (unsigned i = 0; i < _pareto_front.size(); ++i)
        {
          os << gen << " " << i << " ";
          for (unsigned j = 0; j < _pareto_front[i]->fit().objs().size(); ++j)
          {
            os << _pareto_front[i]->fit().obj(j) << " ";
          }
          os << std::endl;;
        }
      }

      const raw_pop_t& getPopulation() const
      {
        return _pop;
      };

      const raw_pop_t& getArchive() const
			{
				return _archive;
			};

    protected:
      pareto_t _pareto_front;
      raw_pop_t _pop;			// Population of the search
      raw_pop_t _archive;	// Archive for Novelty Search
    };
  }
}
#endif
