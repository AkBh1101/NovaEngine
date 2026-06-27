#include <bits/stdc++.h>
#include <chrono>
using namespace std;
using namespace std::chrono;

const int GRID_SIZE      = 36;
const int START_COINS    = 10;
const int COIN_CAP       = 30;
const int TURN_LIMIT     = 400;

enum TileKind{PLAIN=0,COIN_UP=1,COIN_DOWN=2,DICE_BOOST=3,
              LEAP_AHEAD=4,FALL_BACK=5,LOSE_TURN=6,BONUS_TURN=7,
              EVENT=8,ORIGIN=9,GOAL=10};

struct Tile{int id;TileKind kind;int val;string icon,label,hint;};

Tile GRID[GRID_SIZE]={
    {0,ORIGIN,0,"H","Home","Game starts here"},
    {1,PLAIN,0,"M","Meadow","A peaceful meadow"},
    {2,COIN_UP,3,"Sn","Snack Stand","Found snacks! +3"},
    {3,PLAIN,0,"Fl","Flower Patch","Lovely flowers"},
    {4,LEAP_AHEAD,4,"Cr","Quick Ride","Hop in! +4 cells"},
    {5,PLAIN,0,"Pi","Pine Tree","Cool shade"},
    {6,COIN_DOWN,-3,"Pz","Pizza Stall","Bought pizza -3"},
    {7,DICE_BOOST,0,"Ca","Casino Tent","Upgrade to 12-die!"},
    {8,PLAIN,0,"Gv","Gravel Path","Keep walking"},
    {9,COIN_UP,5,"Rt","Ring Toss","You won! +5"},
    {10,LOSE_TURN,0,"Tf","Traffic Jam","Skip your turn"},
    {11,PLAIN,0,"Su","Sunflower","Beautiful view"},
    {12,COIN_DOWN,-5,"Lw","Lost Wallet","Oops! Lost -5"},
    {13,EVENT,0,"Cd","Event Card","Draw a card!"},
    {14,PLAIN,0,"Cm","Campsite","Rest a moment"},
    {15,COIN_UP,4,"Gf","Gift Box","Surprise gift! +4"},
    {16,FALL_BACK,-3,"Mb","Missed Bus","Missed bus! -3 cells"},
    {17,PLAIN,0,"Ck","Creek","Cool creek"},
    {18,BONUS_TURN,0,"Lk","Lucky Clover","Extra turn!"},
    {19,PLAIN,0,"Ps","Picnic Spot","Perfect picnic spot"},
    {20,COIN_DOWN,-4,"Tx","Taxi Home","Took taxi -4"},
    {21,PLAIN,0,"Rb","Rainbow","Beautiful rainbow"},
    {22,COIN_UP,6,"Tr","Tournament","Won tourney! +6"},
    {23,LEAP_AHEAD,3,"Ft","Fast Track","Speed ahead! +3"},
    {24,EVENT,0,"Cd","Event Card","Draw a card!"},
    {25,PLAIN,0,"Fg","Fairground","Fun fair nearby"},
    {26,LOSE_TURN,0,"Rs","Rest Stop","Too tired! Skip"},
    {27,DICE_BOOST,0,"Sb","Star Bonus","Upgrade to 12-die!"},
    {28,COIN_DOWN,-3,"Dl","Long Delay","Delayed! -3"},
    {29,PLAIN,0,"Gd","Garden","Lovely garden"},
    {30,COIN_UP,4,"Ms","Music Show","Awesome show! +4"},
    {31,FALL_BACK,-4,"Rn","Rain Shower","Wet! -4 cells"},
    {32,BONUS_TURN,0,"Eb","Energy Boost","Extra turn!"},
    {33,EVENT,0,"Cd","Event Card","Draw a card!"},
    {34,PLAIN,0,"Cs","Carousel","Almost there!"},
    {35,GOAL,0,"FN","Finish!","You made it!"},
};

struct CardAction{string label;int coin_delta,jump;bool freeze,again;string hint;};
const vector<CardAction> DECK={
    {"Picnic Feast",+3,0,false,false,"Feast! +3 money"},
    {"Storm Warning",-2,0,false,false,"Storm! -2 money"},
    {"Shortcut",0,+3,false,false,"Shortcut! +3 cells"},
    {"Wrong Path",0,-3,false,false,"Wrong path! -3 cells"},
    {"Second Wind",0,0,false,true,"Extra turn!"},
    {"Sunburn",0,0,true,false,"Skip turn!"},
    {"Coupon",+4,0,false,false,"Coupon! +4 money"},
    {"Drop Backpack",-3,0,false,false,"Dropped stuff! -3"},
};

const int ITEM_COUNT=5;
struct Collectible{int tile_id;string tag;int bonus;};
const Collectible LOOT[ITEM_COUNT]={
    {5,"Compass",2},{11,"Sunscreen",2},{17,"Water Bottle",3},
    {21,"Picnic Blanket",2},{29,"Trail Map",3}
};
int loot_at(int pos){
    for(int i=0;i<ITEM_COUNT;i++) if(LOOT[i].tile_id==pos) return i;
    return -1;
}

struct PlayerState{int pos,coins,dice_tier;};

// ── Prefix Sums ──────────────────────────────────────────────
int CUM_VALS[GRID_SIZE+1];
void init_prefix(){
    CUM_VALS[0]=0;
    for(int i=0;i<GRID_SIZE;i++)
        CUM_VALS[i+1]=CUM_VALS[i]+GRID[i].val;
}
int range_sum(int lo,int hi){
    if(lo>hi) return 0;
    lo=max(0,lo); hi=min(GRID_SIZE-1,hi);
    return CUM_VALS[hi+1]-CUM_VALS[lo];
}

PlayerState resolve_tile(int pos,int coins,int dice_tier){
    if(pos<0||pos>=GRID_SIZE) return {pos,coins,dice_tier};
    const Tile& t=GRID[pos];
    switch(t.kind){
        case COIN_UP: case COIN_DOWN: coins+=t.val; break;
        case DICE_BOOST: dice_tier=1; break;
        case LEAP_AHEAD: pos=min(pos+t.val,GRID_SIZE-1); break;
        case FALL_BACK:  pos=max(pos+t.val,0); break;
        case EVENT:{int idx=pos%(int)DECK.size();
            coins+=DECK[idx].coin_delta;
            pos=max(0,min(GRID_SIZE-1,pos+DECK[idx].jump));break;}
        default: break;
    }
    if(coins<=0){coins=START_COINS;pos=0;dice_tier=0;}
    coins=min(coins,COIN_CAP);
    return {pos,coins,dice_tier};
}

// ── Sprague-Grundy ───────────────────────────────────────────
unordered_map<int,int> sg_cache;
unordered_set<int> sg_stack;
inline int pack(int pos,int coins,int dt){return pos*(COIN_CAP+1)*2+coins*2+dt;}
int mex_of(vector<int>& vals){
    unordered_set<int> seen(vals.begin(),vals.end());
    int m=0; while(seen.count(m))m++; return m;
}
int sg_value(int pos,int coins,int dt){
    coins=min(coins,COIN_CAP);
    if(pos>=GRID_SIZE-1) return 0;
    int key=pack(pos,coins,dt);
    auto it=sg_cache.find(key); if(it!=sg_cache.end()) return it->second;
    if(sg_stack.count(key)) return 0;
    sg_stack.insert(key);
    int faces=(dt==0)?6:12;
    vector<int> child_vals;
    for(int r=1;r<=faces;r++){
        int np=pos+r; if(np>GRID_SIZE-1) continue;
        PlayerState ns=resolve_tile(np,coins,dt);
        child_vals.push_back(ns.pos>=GRID_SIZE-1?0:sg_value(ns.pos,ns.coins,ns.dice_tier));
    }
    int g=child_vals.empty()?0:mex_of(child_vals);
    sg_cache[key]=g; sg_stack.erase(key);
    return g;
}

// ── Binary Search: minimum coins to be in winning position ───
bool is_winning(int pos,int coins,int dt){return sg_value(pos,min(coins,COIN_CAP),dt)!=0;}
int min_coins_to_win(int pos,int dt){
    int lo=1,hi=COIN_CAP,ans=COIN_CAP;
    while(lo<=hi){
        int mid=(lo+hi)/2;
        if(is_winning(pos,mid,dt)){ans=mid;hi=mid-1;}
        else lo=mid+1;
    }
    return ans;
}

// ── BFS: fewest moves to finish ──────────────────────────────
vector<int> bfs_to_goal(){
    vector<int> d(GRID_SIZE,INT_MAX);
    queue<int> q;
    d[GRID_SIZE-1]=0;
    vector<vector<int>> back(GRID_SIZE);
    for(int src=0;src<GRID_SIZE-1;src++){
        for(int r=1;r<=12;r++){
            int raw=src+r; if(raw>=GRID_SIZE) break;
            PlayerState ns=resolve_tile(raw,START_COINS,0);
            int dst=min(ns.pos,GRID_SIZE-1);
            if(dst!=src) back[dst].push_back(src);
        }
    }
    q.push(GRID_SIZE-1);
    while(!q.empty()){
        int u=q.front();q.pop();
        for(int v:back[u])
            if(d[v]==INT_MAX){d[v]=d[u]+1;q.push(v);}
    }
    return d;
}

// ── Dijkstra: lowest-risk path to finish ─────────────────────
int tile_risk(int raw){
    const Tile& t=GRID[raw];
    int cost=1;
    switch(t.kind){
        case COIN_DOWN:  cost+=abs(t.val)*2; break;
        case LOSE_TURN:  cost+=6; break;
        case FALL_BACK:  cost+=5+abs(t.val); break;
        case EVENT:      cost+=3; break;
        case COIN_UP:    cost=max(1,cost-t.val/2); break;
        case LEAP_AHEAD: cost=1; break;
        case BONUS_TURN: cost=1; break;
        default: break;
    }
    return max(1,cost);
}
vector<int> dijkstra_safest(){
    vector<vector<pair<int,int>>> back(GRID_SIZE);
    for(int src=0;src<GRID_SIZE-1;src++){
        for(int r=1;r<=12;r++){
            int raw=src+r; if(raw>=GRID_SIZE) break;
            PlayerState ns=resolve_tile(raw,START_COINS,0);
            int dst=min(ns.pos,GRID_SIZE-1);
            if(dst!=src) back[dst].push_back({src,tile_risk(raw)});
        }
    }
    const int BIG=1e9;
    vector<int> dist(GRID_SIZE,BIG);
    priority_queue<pair<int,int>,vector<pair<int,int>>,greater<pair<int,int>>> pq;
    dist[GRID_SIZE-1]=0; pq.push({0,GRID_SIZE-1});
    while(!pq.empty()){
        auto [d,u]=pq.top(); pq.pop();
        if(d!=dist[u]) continue;
        for(auto [v,w]:back[u])
            if(dist[v]>d+w){dist[v]=d+w;pq.push({dist[v],v});}
    }
    return dist;
}

// ── Minimax ───────────────────────────────────────────────────
int minimax_eval(int pos,int coins,int dt,int depth,bool maxer){
    if(pos>=GRID_SIZE-1) return maxer?10000:-10000;
    if(depth==0) return pos;
    int faces=(dt==0)?6:12;
    if(maxer){
        int best=INT_MIN;
        for(int r=1;r<=faces;r++){
            int raw=pos+r; if(raw>=GRID_SIZE) continue;
            PlayerState ns=resolve_tile(raw,coins,dt);
            best=max(best,minimax_eval(ns.pos,ns.coins,ns.dice_tier,depth-1,false));
        }
        return best==INT_MIN?pos:best;
    } else {
        int worst=INT_MAX;
        for(int r=1;r<=faces;r++){
            int raw=pos+r; if(raw>=GRID_SIZE) continue;
            PlayerState ns=resolve_tile(raw,coins,dt);
            worst=min(worst,minimax_eval(ns.pos,ns.coins,ns.dice_tier,depth-1,true));
        }
        return worst==INT_MAX?pos:worst;
    }
}
int minimax_pick(int pos,int coins,int dt,int depth=4){
    int faces=(dt==0)?6:12;
    int pick=1,top=INT_MIN;
    for(int r=1;r<=faces;r++){
        int raw=pos+r; if(raw>=GRID_SIZE) continue;
        PlayerState ns=resolve_tile(raw,coins,dt);
        int sc=minimax_eval(ns.pos,ns.coins,ns.dice_tier,depth-1,false);
        if(sc>top){top=sc;pick=r;}
    }
    return pick;
}

// ── Lookahead ─────────────────────────────────────────────────
int foresight_score(int pos,int coins,int dt,int depth){
    if(pos>=GRID_SIZE-1) return 100000+coins;
    if(depth==0) return pos*1000+coins;
    int faces=(dt==0)?6:12;
    int best=INT_MIN;
    for(int r=1;r<=faces;r++){
        int raw=pos+r; if(raw>=GRID_SIZE) continue;
        PlayerState ns=resolve_tile(raw,coins,dt);
        best=max(best,foresight_score(ns.pos,ns.coins,ns.dice_tier,depth-1));
    }
    return best==INT_MIN?pos*1000+coins:best;
}
int foresight_pick(int pos,int coins,int dt,int depth=4){
    int faces=(dt==0)?6:12;
    int pick=1,top=INT_MIN;
    for(int r=1;r<=faces;r++){
        int raw=pos+r; if(raw>=GRID_SIZE) continue;
        PlayerState ns=resolve_tile(raw,coins,dt);
        int sc=foresight_score(ns.pos,ns.coins,ns.dice_tier,depth-1);
        if(sc>top){top=sc;pick=r;}
    }
    return pick;
}

// ── Move struct + enumeration ─────────────────────────────────
struct RollOption{
    int roll,next_pos,next_coins,next_dt,sg_val,mm_score;
    bool is_win,freezes,repeats;
    string tile_name,tile_icon,tile_hint,card_name,card_hint;
    bool picked_loot; int loot_id; string loot_name;
};

vector<RollOption> enumerate_moves(int pos,int coins,int dt,int mask=0){
    vector<RollOption> opts;
    int faces=(dt==0)?6:12;
    for(int r=1;r<=faces;r++){
        int raw=pos+r; if(raw>GRID_SIZE-1) continue;
        const Tile& t=GRID[raw];
        PlayerState ns=resolve_tile(raw,coins,dt);
        string cn="",cd=""; bool fr=false,rp=false;
        if(t.kind==EVENT){int idx=raw%(int)DECK.size();
            cn=DECK[idx].label;cd=DECK[idx].hint;fr=DECK[idx].freeze;rp=DECK[idx].again;}
        if(t.kind==LOSE_TURN) fr=true;
        if(t.kind==BONUS_TURN) rp=true;
        int gv=ns.pos>=GRID_SIZE-1?0:sg_value(ns.pos,ns.coins,ns.dice_tier);
        int mv=minimax_eval(ns.pos,ns.coins,ns.dice_tier,3,false);
        int li=loot_at(raw);
        bool got=(li>=0&&!((mask>>li)&1));
        string ln=got?LOOT[li].tag:"";
        opts.push_back({r,ns.pos,ns.coins,ns.dice_tier,gv,mv,(gv==0),fr,rp,
                        t.label,t.icon,t.hint,cn,cd,got,li,ln});
    }
    sort(opts.begin(),opts.end(),[](const RollOption&a,const RollOption&b){
        if(a.is_win!=b.is_win) return a.is_win>b.is_win;
        return a.next_pos>b.next_pos;
    });
    return opts;
}
void emit_moves(const vector<RollOption>& opts){
    cout<<"MOVES_START\n";
    for(auto& o:opts)
        cout<<"MOVE|"<<o.roll<<"|"<<o.next_pos<<"|"<<o.next_coins<<"|"<<o.next_dt
            <<"|"<<o.sg_val<<"|"<<(o.is_win?"WIN":"LOSS")
            <<"|"<<o.tile_name<<"|"<<o.tile_icon<<"|"<<o.tile_hint
            <<"|"<<o.card_name<<"|"<<o.card_hint
            <<"|"<<(o.freezes?"1":"0")<<"|"<<(o.repeats?"1":"0")
            <<"|"<<o.mm_score
            <<"|"<<(o.picked_loot?"1":"0")<<"|"<<o.loot_id<<"|"<<o.loot_name<<"\n";
    cout<<"MOVES_END\n";
}

void emit_bfs(){
    auto d=bfs_to_goal();
    cout<<"BFS_START\n";
    for(int i=0;i<GRID_SIZE;i++)
        cout<<"BFS|"<<i<<"|"<<(d[i]==INT_MAX?-1:d[i])<<"\n";
    cout<<"BFS_END\n";
}
void emit_dijkstra(){
    auto d=dijkstra_safest();
    cout<<"DIJKSTRA_START\n";
    for(int i=0;i<GRID_SIZE;i++)
        cout<<"DIJKSTRA|"<<i<<"|"<<(d[i]>=1000000000?-1:d[i])<<"\n";
    cout<<"DIJKSTRA_END\n";
}
void emit_prefix(){
    cout<<"PREFIX_START\n";
    for(int i=0;i<GRID_SIZE;i++)
        cout<<"PREFIX|"<<i<<"|"<<range_sum(0,i)<<"\n";
    cout<<"PREFIX_END\n";
}

void emit_timings(int pos,int coins,int dt){
    cout<<"TIMING_START\n";
    sg_cache.clear(); sg_stack.clear();
    auto t0=high_resolution_clock::now();
    int gv=sg_value(pos,coins,dt);
    auto t1=high_resolution_clock::now();
    cout<<"TIMING|Grundy (Sprague-Grundy)|O(B*M*D) ≈ O(2232*faces)|"
        <<duration_cast<microseconds>(t1-t0).count()
        <<"us|G="<<gv<<"\n";

    auto t2=high_resolution_clock::now();
    int mc=min_coins_to_win(pos,dt);
    auto t3=high_resolution_clock::now();
    cout<<"TIMING|Binary Search (min winning coins)|O(log M * B*M*D)|"
        <<duration_cast<microseconds>(t3-t2).count()
        <<"us|MinCoins="<<mc<<"\n";

    auto t4=high_resolution_clock::now();
    init_prefix();
    auto t5=high_resolution_clock::now();
    int pv=range_sum(pos,GRID_SIZE-1);
    cout<<"TIMING|Prefix Sum (build+query)|Build O(N), Query O(1)|"
        <<duration_cast<microseconds>(t5-t4).count()
        <<"us|RangeGain["<<pos<<"-35]="<<pv<<"\n";

    auto t6=high_resolution_clock::now();
    auto bd=bfs_to_goal();
    auto t7=high_resolution_clock::now();
    int bv=bd[pos]==INT_MAX?-1:bd[pos];
    cout<<"TIMING|BFS (shortest path to finish)|O(V+E) = O("<<GRID_SIZE<<"*12)|"
        <<duration_cast<microseconds>(t7-t6).count()
        <<"us|MinMoves="<<bv<<"\n";

    auto t8=high_resolution_clock::now();
    int fp=foresight_pick(pos,coins,dt,4);
    auto t9=high_resolution_clock::now();
    cout<<"TIMING|Minimax (depth=4)|O(D^4) ≈ O(20736)|"
        <<duration_cast<microseconds>(t9-t8).count()
        <<"us|BestRoll="<<fp<<"\n";

    auto t10=high_resolution_clock::now();
    auto risk=dijkstra_safest();
    auto t11=high_resolution_clock::now();
    int rv=risk[pos]>=1000000000?-1:risk[pos];
    cout<<"TIMING|Dijkstra (minimum-risk path)|O(E log V)|"
        <<duration_cast<microseconds>(t11-t10).count()
        <<"us|MinRisk="<<rv<<"\n";

    cout<<"TIMING_END\n";
}

void run_simulation(int p1p,int p1c,int p1d,int p2p,int p2c,int p2d){
    cout<<"SIM_START\n";
    int turn=1,active=1;
    bool p1freeze=false,p2freeze=false;
    while(turn<=TURN_LIMIT){
        int pos=(active==1)?p1p:p2p;
        int cns=(active==1)?p1c:p2c;
        int dt=(active==1)?p1d:p2d;
        if(pos>=GRID_SIZE-1) break;
        bool& frozen=(active==1)?p1freeze:p2freeze;
        if(frozen){cout<<"SIM_SKIP|"<<turn<<"|"<<active<<"\n";
            frozen=false;active=3-active;turn++;continue;}
        auto opts=enumerate_moves(pos,cns,dt);
        if(opts.empty()){active=3-active;turn++;continue;}
        const RollOption& top=opts[0];
        cout<<"SIM_STEP|"<<turn<<"|"<<active
            <<"|"<<pos<<"|"<<cns<<"|"<<dt<<"|"<<top.roll
            <<"|"<<top.next_pos<<"|"<<top.next_coins<<"|"<<top.next_dt
            <<"|"<<(top.is_win?"WIN":"LOSS")
            <<"|"<<top.tile_name<<"|"<<top.card_name
            <<"|"<<(top.freezes?"1":"0")<<"|"<<(top.repeats?"1":"0")
            <<"|"<<top.sg_val<<"\n";
        if(active==1){p1p=top.next_pos;p1c=top.next_coins;p1d=top.next_dt;}
        else         {p2p=top.next_pos;p2c=top.next_coins;p2d=top.next_dt;}
        int cp=(active==1)?p1p:p2p;
        if(cp>=GRID_SIZE-1){cout<<"SIM_WIN|"<<active<<"|"<<turn<<"\n";break;}
        if(top.freezes){bool& opp=(active==1)?p2freeze:p1freeze;opp=true;}
        if(top.repeats){turn++;continue;}
        active=3-active;turn++;
    }
    cout<<"SIM_END|"<<p1p<<"|"<<p1c<<"|"<<p1d
        <<"|"<<p2p<<"|"<<p2c<<"|"<<p2d<<"\n";
}

enum Tactic{RAND=0,GREEDY=1,MMBOT=2,SGBOT=3};
const vector<string> TACTIC_NAMES={"Random","Greedy","Minimax","Grundy"};

int pick_roll(Tactic t,int pos,int coins,int dt,mt19937& rng){
    vector<RollOption> opts=enumerate_moves(pos,coins,dt);
    if(opts.empty()) return 1;
    if(t==SGBOT) return opts[0].roll;
    if(t==MMBOT){
        const RollOption* best=&opts[0];
        for(const auto& o:opts)
            if(o.next_pos>best->next_pos||(o.next_pos==best->next_pos&&o.mm_score>best->mm_score))
                best=&o;
        return best->roll;
    }
    if(t==GREEDY){
        const RollOption* best=&opts[0];
        for(const auto& o:opts)
            if(o.next_pos>best->next_pos||(o.next_pos==best->next_pos&&o.next_coins>best->next_coins))
                best=&o;
        return best->roll;
    }
    uniform_int_distribution<int> rnd(0,(int)opts.size()-1);
    return opts[rnd(rng)].roll;
}

struct GameResult{int winner,rounds,p1end,p2end;};
GameResult run_match(Tactic t1,Tactic t2,mt19937& rng){
    int p1p=0,p2p=0,p1c=START_COINS,p2c=START_COINS,p1d=0,p2d=0;
    bool p1fr=false,p2fr=false;
    int active=1;
    for(int turn=1;turn<=TURN_LIMIT;turn++){
        int& pos=(active==1)?p1p:p2p;
        int& cns=(active==1)?p1c:p2c;
        int& dt =(active==1)?p1d:p2d;
        bool& fr=(active==1)?p1fr:p2fr;
        if(pos>=GRID_SIZE-1) return {active,turn,p1c,p2c};
        if(fr){fr=false;active=3-active;continue;}
        int roll=pick_roll((active==1)?t1:t2,pos,cns,dt,rng);
        int raw=pos+roll;
        if(raw<=GRID_SIZE-1){
            PlayerState ns=resolve_tile(raw,cns,dt);
            const Tile& t=GRID[raw];
            bool sk=(t.kind==LOSE_TURN),ex=(t.kind==BONUS_TURN);
            if(t.kind==EVENT){int idx=raw%(int)DECK.size();sk=DECK[idx].freeze;ex=DECK[idx].again;}
            pos=ns.pos; cns=ns.coins; dt=ns.dice_tier;
            if(pos>=GRID_SIZE-1) return {active,turn,p1c,p2c};
            if(sk){bool& opp=(active==1)?p2fr:p1fr;opp=true;}
            if(ex) continue;
        }
        active=3-active;
    }
    if(p1p!=p2p) return {p1p>p2p?1:2,TURN_LIMIT,p1c,p2c};
    return {p1c>=p2c?1:2,TURN_LIMIT,p1c,p2c};
}

void emit_tournament(){
    const int N=TACTIC_NAMES.size(), MATCHES=20;
    vector<int> w(N,0),g(N,0),ts(N,0),ms(N,0);
    mt19937 rng(42);
    for(int a=0;a<N;a++){
        for(int b=0;b<N;b++){
            if(a==b) continue;
            for(int r=0;r<MATCHES;r++){
                GameResult res=run_match((Tactic)a,(Tactic)b,rng);
                g[a]++;g[b]++;
                ts[a]+=res.rounds;ts[b]+=res.rounds;
                ms[a]+=res.p1end;ms[b]+=res.p2end;
                if(res.winner==1) w[a]++; else w[b]++;
            }
        }
    }
    cout<<"TOURNAMENT_START\n";
    for(int i=0;i<N;i++){
        double wr=g[i]?100.0*w[i]/g[i]:0.0;
        double at=g[i]?1.0*ts[i]/g[i]:0.0;
        double am=g[i]?1.0*ms[i]/g[i]:0.0;
        cout<<"TOURNAMENT|"<<TACTIC_NAMES[i]<<"|"<<w[i]<<"|"<<g[i]
            <<"|"<<fixed<<setprecision(1)<<wr<<"|"<<at<<"|"<<am<<"\n";
    }
    cout<<"TOURNAMENT_END\n";
}

void emit_tiles(){
    cout<<"CELLS_START\n";
    for(int i=0;i<GRID_SIZE;i++){
        auto& t=GRID[i];
        cout<<"CELL|"<<t.id<<"|"<<(int)t.kind<<"|"<<t.val
            <<"|"<<t.icon<<"|"<<t.label<<"|"<<t.hint<<"\n";
    }
    cout<<"CELLS_END\n";
}
void emit_graph(){
    cout<<"GRAPH_START\n";
    for(int i=0;i<GRID_SIZE-1;i++) cout<<"EDGE|"<<i<<"|"<<(i+1)<<"|normal\n";
    vector<tuple<int,int,string>> specials={
        {4,8,"Quick Ride"},{16,13,"Missed Bus"},{23,26,"Fast Track"},
        {31,27,"Rain"},{13,16,"Card-WP"},{24,21,"Card-WP2"},
        {33,30,"Card-SC"},{18,20,"Lucky+skip"}};
    for(const auto& e:specials)
        cout<<"EDGE|"<<get<0>(e)<<"|"<<get<1>(e)<<"|"<<get<2>(e)<<"\n";
    cout<<"GRAPH_END\n";
}

int main(int argc,char* argv[]){
    ios::sync_with_stdio(false); cin.tie(nullptr);
    init_prefix();
    if(argc<2){cerr<<"Usage: engine <mode>\n";return 1;}
    string mode=argv[1];
    if(mode=="cellinfo")  {emit_tiles();return 0;}
    if(mode=="graph")     {emit_graph();return 0;}
    if(mode=="bfs")       {emit_bfs();return 0;}
    if(mode=="dijkstra")  {emit_dijkstra();return 0;}
    if(mode=="prefix")    {emit_prefix();return 0;}
    if(mode=="tournament"){emit_tournament();return 0;}
    if(mode=="simulate"){
        int p1p=0,p1c=START_COINS,p1d=0,p2p=0,p2c=START_COINS,p2d=0;
        cin>>p1p>>p1c>>p1d>>p2p>>p2c>>p2d;
        run_simulation(p1p,p1c,p1d,p2p,p2c,p2d);
        return 0;
    }
    int pos=0,coins=START_COINS,dt=0;
    cin>>pos>>coins>>dt;
    coins=min(coins,COIN_CAP);
    if(mode=="timings")  {emit_timings(pos,coins,dt);return 0;}
    if(mode=="binsearch"){
        cout<<"BINSEARCH|"<<min_coins_to_win(pos,dt)<<"\n";
        return 0;
    }
    if(mode=="grundy"){
        int g=sg_value(pos,coins,dt);
        cout<<"GRUNDY|"<<g<<"\n";
        cout<<"STATE|"<<(g!=0?"WINNING":"LOSING")<<"\n";
        emit_moves(enumerate_moves(pos,coins,dt,0));
    } else if(mode=="moves"){
        emit_moves(enumerate_moves(pos,coins,dt,0));
    } else if(mode=="apply"){
        int roll; cin>>roll;
        int raw=pos+roll;
        if(raw>GRID_SIZE-1){cout<<"INVALID|overshoot\n";}
        else{
            PlayerState ns=resolve_tile(raw,coins,dt);
            const Tile& t=GRID[raw];
            bool fr=(t.kind==LOSE_TURN),rp=(t.kind==BONUS_TURN);
            string cn="",cd="";
            if(t.kind==EVENT){int idx=raw%(int)DECK.size();
                cn=DECK[idx].label;cd=DECK[idx].hint;fr=DECK[idx].freeze;rp=DECK[idx].again;}
            int li=loot_at(raw);
            string ln=(li>=0)?LOOT[li].tag:"";
            cout<<"RESULT|"<<ns.pos<<"|"<<ns.coins<<"|"<<ns.dice_tier
                <<"|"<<t.icon<<" "<<t.label<<"|"<<t.hint
                <<"|"<<cn<<"|"<<cd
                <<"|"<<(fr?"1":"0")<<"|"<<(rp?"1":"0")
                <<"|"<<ln<<"\n";
        }
    }
    return 0;
}
