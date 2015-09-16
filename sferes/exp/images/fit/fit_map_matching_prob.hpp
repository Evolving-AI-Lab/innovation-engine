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

#ifndef FIT_MAP_MATCHING_PROB_HPP
#define FIT_MAP_MATCHING_PROB_HPP

#include "fit_deep_learning.hpp"

#include <boost/accumulators/accumulators.hpp>
#include <boost/accumulators/statistics/stats.hpp>

// Headers specifics to the computations we need
#include <boost/accumulators/statistics/mean.hpp>
#include <boost/accumulators/statistics/max.hpp>


#define FIT_MAP_MATCHING_PROB(Name) SFERES_FITNESS(Name, sferes::fit::FitDeepLearning)

namespace sferes
{
  namespace fit
  {
    SFERES_FITNESS(FitMapMatchingProb, sferes::fit::FitDeepLearning)
    {
    private:

    	void _setProbabilityList(const cv::Mat& image)
			{
				this->initCaffeNet();	//Initialize caffe

				// Initialize test network
				shared_ptr<Net<float> > caffe_test_net = shared_ptr<Net<float> >( new Net<float>(Params::image::model_definition));

				// Get the trained model
				caffe_test_net->CopyTrainedLayersFrom(Params::image::pretrained_model);

				// Run ForwardPrefilled
				float loss;

				// We do not use 10 crops here, only 1 single center crop
				// Add images and labels manually to the ImageDataLayer
				vector<int> labels(1, 0);
				vector<cv::Mat> images;

				// Create a single crop of size 227x227
				// And add that image to the list of images
				images.push_back(image);

				// Classify images
				// 2015-01-16: Using this Memory Data Layer from this Caffe branch:
				// https://github.com/BVLC/caffe/pull/1416
				const shared_ptr<MemoryDataLayer<float> > memory_data_layer =
							boost::static_pointer_cast<MemoryDataLayer<float> >(
									caffe_test_net->layer_by_name("data"));

			  memory_data_layer->AddMatVector(images, labels);

				// Make a forward pass
				const vector<Blob<float>*>& result = caffe_test_net->ForwardPrefilled(&loss);

				// Clear the probability in case it is called twice
				_prob.clear();
				_prob.resize(Params::image::num_categories);

				// Set the values for this image
				// prob
				_set_values_at_fc_layer(	caffe_test_net,
							Params::image::target_layer::name,
							Params::image::target_layer::start_index,
							Params::image::target_layer::num_outputs
						);
			}

    	void _set_values_at_fc_layer(const shared_ptr<Net<float> >& caffe_test_net,
    						const std::string& layer_name, const int start_index, const int num_outputs)
			{
				// Extract out a specific unit
				// Get the blob at conv1 layer
				const shared_ptr<Blob<float> > blob = caffe_test_net->blob_by_name(layer_name);

				// Make sure the number of cells in MAP-Elites correspond to the channels
				// For example, for AlexNet, conv1 layer has 96 channels.
				assert(blob->channels() == num_outputs);

				if (Params::image::use_crops)
				{
					// If use 10 crops, we have to average the predictions of 10 crops
					for(int i = 0; i < num_outputs; ++i)
					{
						// Get the average of 10 crops
						boost::accumulators::accumulator_set<double, boost::accumulators::stats<boost::accumulators::tag::mean> > avg;

						// 10 crops
						for (int c = 0; c < 10; c++)
						{
							float v = blob->data_at(c, i, 0, 0);	// There is only one output unit per channel
							avg(v);
						}

						double mean = boost::accumulators::mean(avg);	// Average of 10 crops

						// This value corresponds to the activation at unit (x, y) on the given channel
						const size_t index = i + start_index;
						this->_prob.at(index) = mean;
					}
				}
				else	// Single-crop
				{
					// If use 10 crops, we have to average the predictions of 10 crops
					for(int i = 0; i < num_outputs; ++i)
					{
						float v = blob->data_at(0, i, 0, 0);	// There is only one output unit per channel

						// This value corresponds to the activation at unit (x, y) on the given channel
						const size_t index = i + start_index;
						this->_prob.at(index) = v;
					}
				}
			}

      public:
    	FitMapMatchingProb() : _prob(Params::image::num_categories) { }
			const std::vector<float>& desc() const { return _prob; }

			// Indiv will have the type defined in the main (phen_t)
			template<typename Indiv>
			void eval(const Indiv& ind)
			{
				if (Params::image::color)
				{
					// Convert image to BGR before evaluating
					cv::Mat output;

					// Convert HLS into BGR because imwrite uses BGR color space
					cv::cvtColor(ind.image(), output, CV_HLS2BGR);

					// Create an empty list to store get 1000 probabilities
					_setProbabilityList(output);
				}
				else	// Grayscale
				{
					// Create an empty list to store get 1000 probabilities
					_setProbabilityList(ind.image());
				}
			}

			float value(int category) const
			{
				assert(category < _prob.size());
				return _prob[category];
			}

			float value() const
			{
				return this->_value;
			}

			template<class Archive>
			void serialize(Archive & ar, const unsigned int version) {
				sferes::fit::Fitness<Params,  typename stc::FindExact<FitMapMatchingProb<Params, Exact>, Exact>::ret>::serialize(ar, version);
				ar & BOOST_SERIALIZATION_NVP(_prob);
			}

      protected:
			  std::vector<float> _prob; // List of probabilities
    };
  }
}

#endif
