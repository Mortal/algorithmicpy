#include <iostream>
#include <vector>
#include <limits>
#include <algorithm>

constexpr int inf = std::numeric_limits<int>::max();

struct lis {
	// Initialize arrays.
	void begin() {
		L.resize(0);
		old.resize(0);
	}

	// Return the index of the first entry greater than v.
	size_t insertion_point(int v) {
		return std::lower_bound(L.begin(), L.end(), v + 1) - L.begin();
	}

	// Return the index of the last entry in L less than v.
	size_t restore_point(int v) {
		return std::lower_bound(L.begin(), L.end(), v) - L.begin() - 1;
	}

	// Return the length of the longest increasing subsequence.
	size_t size() {
		return L.size();
	}

	// Update L array according to next input element.
	void push(int v) {
		size_t j = insertion_point(v);
		if (j == L.size()) {
			old.push_back(inf);
			L.push_back(v);
		} else {
			old.push_back(L[j]);
			L[j] = v;
		}
		print_L();
	}

	// Backtrack, computing the LIS.
	std::vector<int> end() {
		std::vector<int> result(size());
		if (result.size() == 0) return result;
		size_t n = result.size() - 1;
		while (true) {
			result[n] = L[n];
			size_t j = restore_point(old.back());
			if (old.back() == inf) L.pop_back();
			else L[j] = old.back();
			old.pop_back();
			print_L();
			if (j == n)
				if (n-- == 0)
					break;
		}
		return result;
	}

	// For debugging, print out the L array to standard output.
	void print_L() {
		std::cout << "L:";
		for (int v : L) std::cout << ' ' << v;
		std::cout << std::endl;
	}

	// L[j]: Smallest possible last element
	// of an increasing subsequence of length j.
	std::vector<int> L;
	// old[i]: The element of L that was overwritten
	// when reading element x[i]. Allows reconstruction of
	// past L table using binary search.
	std::vector<int> old;
};

int main() {
	lis l;
	l.begin();
	// Read integers from standard input.
	int v;
	while (std::cin >> v) l.push(v);
	// Compute longest increasing subsequence.
	std::vector<int> r = l.end();
	// Output longest increasing subsequence.
	std::cout << r.size() << ":";
	for (int v : r) std::cout << ' ' << v;
	std::cout << std::endl;
	return 0;
}
