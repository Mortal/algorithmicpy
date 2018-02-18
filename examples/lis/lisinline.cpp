#include <iostream>
#include <vector>
#include <limits>
#include <algorithm>

int main() {
	int inf = std::numeric_limits<int>::max();

	// L[j]: Smallest possible last element
	// of an increasing subsequence of length j.
	std::vector<int> L;
	// old[i]: The element of L that was overwritten
	// when reading element x[i]. Allows reconstruction of
	// past L table using binary search.
	std::vector<int> old;

	// Read integers from standard input.
	int v;
	while (std::cin >> v) {
		size_t j = std::lower_bound(L.begin(), L.end(), v + 1) - L.begin();
		if (j == L.size()) {
			old.push_back(inf);
			L.push_back(v);
		} else {
			old.push_back(L[j]);
			L[j] = v;
		}
	}
	// Compute longest increasing subsequence.
	std::vector<int> result(L.size());
	size_t n = result.size();
	while (n) {
		result[n-1] = L[n-1];
		size_t j = std::lower_bound(L.begin(), L.end(), old.back()) - L.begin() - 1;
		if (old.back() == inf) L.pop_back();
		else L[j] = old.back();
		old.pop_back();
		if (j == n-1) n--;
	}

	// Output longest increasing subsequence.
	std::cout << result.size() << ":";
	for (int v : result) std::cout << ' ' << v;
	std::cout << std::endl;
	return 0;
}
