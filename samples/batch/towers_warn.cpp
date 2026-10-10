// Accepted, but g++ -Wall warns: an unused variable.
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int n, k;
ll A, B;
vector<ll> x, s, L, R;

bool check(ll P) {
    L.clear(), R.clear();
    for (int i = 0; i < n; i++) {
        ll l = max(A, x[i] - P * s[i]), r = min(B, x[i] + P * s[i]);
        if (l <= r) L.push_back(l), R.push_back(r + 1);
    }
    if ((int)L.size() < k) return false;
    sort(L.begin(), L.end()), sort(R.begin(), R.end());
    const ll INF = LLONG_MAX;
    ll prev = A;
    int cur = 0;
    size_t i = 0, j = 0;
    while (i < L.size() || j < R.size()) {
        ll pos = min(i < L.size() ? L[i] : INF, j < R.size() ? R[j] : INF);
        if (prev <= min(pos - 1, B) && cur < k) return false;     // points prev .. pos-1 have cur towers
        while (i < L.size() && L[i] == pos) cur++, i++;
        while (j < R.size() && R[j] == pos) cur--, j++;
        prev = pos;
    }
    return !(prev <= B && cur < k);
}

int32_t main() {
    cin.tie(0); ios::sync_with_stdio(0);
    int unused;
    cin >> n >> k >> A >> B;
    x.resize(n), s.resize(n);
    for (int i = 0; i < n; i++) cin >> x[i] >> s[i];
    ll lo = 0, hi = 2000000000LL;
    while (lo < hi) {
        ll mid = (lo + hi) / 2;
        if (check(mid)) hi = mid;
        else lo = mid + 1;
    }
    cout << lo << '\n';
    return 0;
}
