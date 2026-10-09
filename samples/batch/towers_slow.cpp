// Time Limit Exceeded: correct, but tries P = 0, 1, 2, ... (sample 5 needs P = 2000000000).
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int n, k;
ll A, B;
vector<ll> x, s;

bool check(ll P) {
    vector<pair<ll, int>> ev;
    for (int i = 0; i < n; i++) {
        ll l = max(A, x[i] - P * s[i]), r = min(B, x[i] + P * s[i]);
        if (l <= r) ev.push_back({l, 1}), ev.push_back({r + 1, -1});
    }
    sort(ev.begin(), ev.end());
    ll prev = A;
    int cur = 0;
    for (size_t i = 0; i < ev.size();) {
        ll pos = ev[i].first;
        if (prev <= min(pos - 1, B) && cur < k) return false;     // points prev .. pos-1 have cur towers
        while (i < ev.size() && ev[i].first == pos) cur += ev[i++].second;
        prev = pos;
    }
    return !(prev <= B && cur < k);
}

int32_t main() {
    cin.tie(0); ios::sync_with_stdio(0);
    cin >> n >> k >> A >> B;
    x.resize(n), s.resize(n);
    for (int i = 0; i < n; i++) cin >> x[i] >> s[i];
    ll lo = 0;
    while (!check(lo)) lo++;
    cout << lo << '\n';
    return 0;
}
