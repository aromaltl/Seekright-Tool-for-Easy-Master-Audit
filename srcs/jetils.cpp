#include <pybind11/pybind11.h>
#include <pybind11/stl.h> 
#include <iostream>
//#include <pybind11/stl_bind.h>

// PYBIND11_MAKE_OPAQUE(std::vector<int>);
// PYBIND11_MAKE_OPAQUE(std::map<std::string, double>);
//#include <Python.h>
// PYBIND11_MAKE_OPAQUE(std::unordered_set<std::string> )

namespace py = pybind11;



void add_keys(py::dict & data, py::list & keys, py::object& obj){
	int i=0;
	int size = static_cast<int>(keys.size());
	bool added = false;
	if (size <1) return;
	while (i < size-1){
		if (!data.contains(keys[i])){
			data[keys[i]]=py::dict {};
			added = true;
			
		}
		
		data = data[keys[i]];
		i++;
	}
	if (added or !data.contains(keys[size-1])){
		data[keys[size-1]]=obj;
	}
}


//a={"0":{"cr":[['2',3],['4',5]]}}
void removeAsset(py::dict & data,int frame_no,std::string & asset,std::string & id,int total_frames) {
	int st = frame_no;
	int last_found = frame_no;
	while (frame_no < total_frames && abs(last_found-frame_no) < 180 && frame_no >=0){
		py::str fr = py::str(std::to_string(frame_no));
		if (data.contains(fr)) {
			py::dict  v = data[fr];
			if (v.contains(asset)){
				py::list l = v[py::str(asset)];
				py::list new_list;


				for(auto &i : l){
					auto v =i.cast<py::list>();

					// std::cout<<std::string(py::str(v[0]))<<id;
					if (std::string(py::str(v[0])) != id) {
						last_found = frame_no;
						new_list.append(v);
					}	
				}
				v[py::str(asset)] = new_list;

			}
		}
		frame_no+=2;	
	}
	frame_no =st-2;
	while (frame_no < total_frames && abs(frame_no-last_found) < 180 && frame_no >=0){
		py::str fr = py::str(std::to_string(frame_no));
		if (data.contains(fr)) {
			py::dict  v = data[fr];
			if (v.contains(asset)){
				py::list l = v[py::str(asset)];
				py::list new_list;


				for(auto &i : l){
					auto v =i.cast<py::list>();

					// std::cout<<std::string(py::str(v[0]))<<id;
					if (std::string(py::str(v[0])) != id) {
						last_found = frame_no;
						new_list.append(v);
					}	
				}
				v[py::str(asset)] = new_list;

			}
		}
		frame_no-=2;
	}
}




PYBIND11_MODULE(jetils, m) {
// py::bind_vector<std::vector<std::>>(m, "VectorInt");
// py::bind_map<std::map<std::string, double>>(m, "MapStringDouble");
// py::bind_set(std::unordered_set<std::string>);
   m.def("removeAsset", &removeAsset, "A function that prints a Python dictionary");
   m.def("add_keys",&add_keys,"add_keys");
}


// void print_dict(py::dict & p,int frame_no) {
// 	if (true){
// 		if (p.contains(py::str(std::to_string(frame_no)))) {
// 			py::list  v = p[py::str(std::to_string(frame_no))];
// 	// 		//auto  v = p[py::str(std::to_string(frame_no))];
// 			v[0]=100;
// 			std::cout<<py::str(v[0]) <<v.ptr()<<"eeeeee"<<p[py::str(std::to_string(frame_no))].ptr()<<"#####$";
// 			for (auto & gg : v){std::cout<<gg;}

// 		}
// 	}


// }

// void remove_key(py::dict d, py::object key_to_remove) {
//     // Print the dictionary before removal
//     std::cout << "Before removal:" << std::endl;
//     for (const auto& item : d) {
//         std::cout << "Key: " << py::str(item.first) << ", Value: " << py::str(item.second) << std::endl;
//     }

//     // Remove the specified key from the dictionary using Python C API
//     if (d.contains(key_to_remove)) {
//         // Convert py::object to PyObject*
//         PyObject* key = key_to_remove.ptr();
//         // Call PyDict_DelItem to remove the key
//         if (PyDict_DelItem(d.ptr(), key) != 0) {
//             PyErr_Print();  // Print error if the key could not be deleted
//         }
//     } else {
//         std::cout << "Key not found in the dictionary." << std::endl;
//     }

//     // Print the dictionary after removal
//     std::cout << "After removal:" << std::endl;
//     for (const auto& item : d) {
//         std::cout << "Key: " << py::str(item.first) << ", Value: " << py::str(item.second) << std::endl;
//     }
// }



// PYBIND11_MODULE(example, m) {
//    m.def("print_dict", &print_dict, "A function that prints a Python dictionary");
// }

