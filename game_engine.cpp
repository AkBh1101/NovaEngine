#include <bits/stdc++.h>
#include <chrono>
using namespace std;
using namespace std::chrono;

const int BOARD_SIZE    = 36;
const int INITIAL_MONEY = 10;
const int MAX_MONEY     = 30;
const int MAX_TURNS     = 400;

enum CellType{NORMAL=0,MONEY_GAIN=1,MONEY_LOSS=2,DIE_UPGRADE=3,
              JUMP_FORWARD=4,JUMP_BACK=5,SKIP_TURN=6,EXTRA_TURN=7,
              CARD=8,START=9,FINISH=10};
struct Cell{int id;CellType type;int value;string emoji,name,desc;};

Cell BOARD[BOARD_SIZE]={
    {0,START,0,"H","Home","Game starts here"},
    {1,NORMAL,0,"M","Meadow","A peaceful meadow"},
    {2,MONEY_GAIN,3,"Sn","Snack Stand","Found snacks! +3"},
    {3,NORMAL,0,"Fl","Flower Patch","Lovely flowers"},
    {4,JUMP_FORWARD,4,"Cr","Quick Ride","Hop in! +4 cells"},
    {5,NORMAL,0,"Pi","Pine Tree","Cool shade"},
    {6,MONEY_LOSS,-3,"Pz","Pizza Stall","Bought pizza -3"},
    {7,DIE_UPGRADE,0,"Ca","Casino Tent","Upgrade to 12-die!"},
    {8,NORMAL,0,"Gv","Gravel Path","Keep walking"},
    {9,MONEY_GAIN,5,"Rt","Ring Toss","You won! +5"},
    {10,SKIP_TURN,0,"Tf","Traffic Jam","Skip your turn"},
    {11,NORMAL,0,"Su","Sunflower","Beautiful view"},
    {12,MONEY_LOSS,-5,"Lw","Lost Wallet","Oops! Lost -5"},
    {13,CARD,0,"Cd","Event Card","Draw a card!"},
    {14,NORMAL,0,"Cm","Campsite","Rest a moment"},
    {15,MONEY_GAIN,4,"Gf","Gift Box","Surprise gift! +4"},
    {16,JUMP_BACK,-3,"Mb","Missed Bus","Missed bus! -3 cells"},
    {17,NORMAL,0,"Ck","Creek","Cool creek"},
    {18,EXTRA_TURN,0,"Lk","Lucky Clover","Extra turn!"},
    {19,NORMAL,0,"Ps","Picnic Spot","Perfect picnic spot"},
    {20,MONEY_LOSS,-4,"Tx","Taxi Home","Took taxi -4"},
    {21,NORMAL,0,"Rb","Rainbow","Beautiful rainbow"},
    {22,MONEY_GAIN,6,"Tr","Tournament","Won tourney! +6"},
    {23,JUMP_FORWARD,3,"Ft","Fast Track","Speed ahead! +3"},
    {24,CARD,0,"Cd","Event Card","Draw a card!"},
    {25,NORMAL,0,"Fg","Fairground","Fun fair nearby"},
    {26,SKIP_TURN,0,"Rs","Rest Stop","Too tired! Skip"},
    {27,DIE_UPGRADE,0,"Sb","Star Bonus","Upgrade to 12-die!"},
    {28,MONEY_LOSS,-3,"Dl","Long Delay","Delayed! -3"},
    {29,NORMAL,0,"Gd","Garden","Lovely garden"},
    {30,MONEY_GAIN,4,"Ms","Music Show","Awesome show! +4"},
    {31,JUMP_BACK,-4,"Rn","Rain Shower","Wet! -4 cells"},
    {32,EXTRA_TURN,0,"Eb","Energy Boost","Extra turn!"},
    {33,CARD,0,"Cd","Event Card","Draw a card!"},
    {34,NORMAL,0,"Cs","Carousel","Almost there!"},
    {35,FINISH,0,"FN","Finish!","You made it!"},
};
struct CardEffect{string name;int money_delta,jump;bool skip,extra;string desc;};
const vector<CardEffect> CARDS={
    {"Picnic Feast",+3,0,false,false,"Feast! +3 money"},
    {"Storm Warning",-2,0,false,false,"Storm! -2 money"},
    {"Shortcut",0,+3,false,false,"Shortcut! +3 cells"},
    {"Wrong Path",0,-3,false,false,"Wrong path! -3 cells"},
    {"Second Wind",0,0,false,true,"Extra turn!"},
    {"Sunburn",0,0,true,false,"Skip turn!"},
    {"Coupon",+4,0,false,false,"Coupon! +4 money"},
    {"Drop Backpack",-3,0,false,false,"Dropped stuff! -3"},
};

// ── Bitmask Power-ups ── 5 items tracked in 5 bits
const int NUM_ITEMS=5;
struct PowerUp{int cell_id;string name;int bonus;};
const PowerUp ITEMS[NUM_ITEMS]={
    {5,"Compass",2},{11,"Sunscreen",2},{17,"Water Bottle",3},
    {21,"Picnic Blanket",2},{29,"Trail Map",3}
};
int item_at_cell(int pos){
    for(int i=0;i<NUM_ITEMS;i++) if(ITEMS[i].cell_id==pos) return i;
    return -1;
}

struct State{int pos,money,die;};

// ── Prefix Sum ── Build O(N), Query O(1)
int PREFIX_GAINS[BOARD_SIZE+1];
void build_prefix_sums(){
    PREFIX_GAINS[0]=0;
    for(int i=0;i<BOARD_SIZE;i++){
        PREFIX_GAINS[i+1]=PREFIX_GAINS[i]+BOARD[i].value;
    }
}
int prefix_query(int L,int R){
    if(L>R) return 0;
    L=max(0,L); R=min(BOARD_SIZE-1,R);
    return PREFIX_GAINS[R+1]-PREFIX_GAINS[L];
}

State apply_cell(int pos,int money,int die){
    if(pos<0||pos>=BOARD_SIZE) return {pos,money,die};
    const Cell& c=BOARD[pos];
    switch(c.type){
        case MONEY_GAIN: case MONEY_LOSS: money+=c.value; break;
        case DIE_UPGRADE: die=1; break;
        case JUMP_FORWARD: pos=min(pos+c.value,BOARD_SIZE-1); break;
        case JUMP_BACK: pos=max(pos+c.value,0); break;
        case CARD:{int idx=pos%(int)CARDS.size();
            money+=CARDS[idx].money_delta;
            pos=max(0,min(BOARD_SIZE-1,pos+CARDS[idx].jump));break;}
        default: break;
    }
    if(money<=0){money=INITIAL_MONEY;pos=0;die=0;}
    money=min(money,MAX_MONEY);
    return {pos,money,die};
}

// ── Grundy ── O(B*M*D) total states, memoized
unordered_map<int,int> g_memo;
unordered_set<int> g_vis;
inline int enc(int pos,int money,int die){return pos*(MAX_MONEY+1)*2+money*2+die;}
int mex(vector<int>& v){
    unordered_set<int> s(v.begin(),v.end());
    int m=0; while(s.count(m))m++; return m;
}
int grundy(int pos,int money,int die){
    money=min(money,MAX_MONEY);
    if(pos>=BOARD_SIZE-1) return 0;
    int k=enc(pos,money,die);
    auto it=g_memo.find(k); if(it!=g_memo.end()) return it->second;
    if(g_vis.count(k)) return 0;
    g_vis.insert(k);
    int faces=(die==0)?6:12;
    vector<int> cg;
    for(int r=1;r<=faces;r++){
        int np=pos+r;
        if(np>BOARD_SIZE-1) continue;
        State ns=apply_cell(np,money,die);
        cg.push_back(ns.pos>=BOARD_SIZE-1?0:grundy(ns.pos,ns.money,ns.die));
    }
    int g=cg.empty()?0:mex(cg);
    g_memo[k]=g; g_vis.erase(k);
    return g;
}

// ── Binary Search: min coins for winning position ── O(log M * Grundy)
bool canWin(int pos,int coins,int die){return grundy(pos,min(coins,MAX_MONEY),die)!=0;}
int binarySearchMinCoins(int pos,int die){
    int lo=1,hi=MAX_MONEY,result=MAX_MONEY;
    while(lo<=hi){
        int mid=(lo+hi)/2;
        if(canWin(pos,mid,die)){result=mid;hi=mid-1;}
        else lo=mid+1;
    }
    return result;
}

// ── BFS: shortest path to finish ── O(V+E)
vector<int> bfs_min_moves(){
    vector<int> dist(BOARD_SIZE,INT_MAX);
    queue<int> q;
    dist[BOARD_SIZE-1]=0;
    vector<vector<int>> rev(BOARD_SIZE);
    for(int src=0;src<BOARD_SIZE-1;src++){
        for(int r=1;r<=12;r++){
            int raw=src+r;
            if(raw>=BOARD_SIZE) break;
            State ns=apply_cell(raw,INITIAL_MONEY,0);
            int dst=min(ns.pos,BOARD_SIZE-1);
            if(dst!=src) rev[dst].push_back(src);
        }
    }
    q.push(BOARD_SIZE-1);
    while(!q.empty()){
        int u=q.front();q.pop();
        for(int v:rev[u])
            if(dist[v]==INT_MAX){dist[v]=dist[u]+1;q.push(v);}
    }
    return dist;
}

// ── Dijkstra: minimum-risk path to finish ── O(E log V)
int landing_risk(int raw){
    const Cell& c=BOARD[raw];
    int cost=1;
    switch(c.type){
        case MONEY_LOSS: cost+=abs(c.value)*2; break;
        case SKIP_TURN: cost+=6; break;
        case JUMP_BACK: cost+=5+abs(c.value); break;
        case CARD: cost+=3; break;
        case MONEY_GAIN: cost=max(1,cost-c.value/2); break;
        case JUMP_FORWARD: cost=1; break;
        case EXTRA_TURN: cost=1; break;
        default: break;
    }
    return max(1,cost);
}
vector<int> dijkstra_min_risk(){
    vector<vector<pair<int,int>>> rev(BOARD_SIZE);
    for(int src=0;src<BOARD_SIZE-1;src++){
        for(int r=1;r<=12;r++){
            int raw=src+r;
            if(raw>=BOARD_SIZE) break;
            State ns=apply_cell(raw,INITIAL_MONEY,0);
            int dst=min(ns.pos,BOARD_SIZE-1);
            if(dst!=src) rev[dst].push_back({src,landing_risk(raw)});
        }
    }
    const int INF=1e9;
    vector<int> dist(BOARD_SIZE,INF);
    priority_queue<pair<int,int>,vector<pair<int,int>>,greater<pair<int,int>>> pq;
    dist[BOARD_SIZE-1]=0;
    pq.push({0,BOARD_SIZE-1});
    while(!pq.empty()){
        auto cur=pq.top(); pq.pop();
        int d=cur.first,u=cur.second;
        if(d!=dist[u]) continue;
        for(auto e:rev[u]){
            int v=e.first,w=e.second;
            if(dist[v]>d+w){
                dist[v]=d+w;
                pq.push({dist[v],v});
            }
        }
    }
    return dist;
}

// ── Minimax: depth-limited AI ── O(D^depth)
int minimax(int pos,int money,int die,int depth,bool maximizer){
    if(pos>=BOARD_SIZE-1) return maximizer?10000:-10000;
    if(depth==0) return pos;
    int faces=(die==0)?6:12;
    if(maximizer){
        int best=INT_MIN;
        for(int r=1;r<=faces;r++){
            int raw=pos+r; if(raw>=BOARD_SIZE) continue;
            State ns=apply_cell(raw,money,die);
            best=max(best,minimax(ns.pos,ns.money,ns.die,depth-1,false));
        }
        return best==INT_MIN?pos:best;
    } else {
        int worst=INT_MAX;
        for(int r=1;r<=faces;r++){
            int raw=pos+r; if(raw>=BOARD_SIZE) continue;
            State ns=apply_cell(raw,money,die);
            worst=min(worst,minimax(ns.pos,ns.money,ns.die,depth-1,true));
        }
        return worst==INT_MAX?pos:worst;
    }
}
int minimaxBestRoll(int pos,int money,int die,int depth=4){
    int faces=(die==0)?6:12;
    int bestRoll=1,bestVal=INT_MIN;
    for(int r=1;r<=faces;r++){
        int raw=pos+r; if(raw>=BOARD_SIZE) continue;
        State ns=apply_cell(raw,money,die);
        int val=minimax(ns.pos,ns.money,ns.die,depth-1,false);
        if(val>bestVal){bestVal=val;bestRoll=r;}
    }
    return bestRoll;
}

// ── Move List ─────────────────────────────────────────────────
int lookaheadScore(int pos,int money,int die,int depth){
    if(pos>=BOARD_SIZE-1) return 100000+money;
    if(depth==0) return pos*1000+money;
    int faces=(die==0)?6:12;
    int best=INT_MIN;
    for(int r=1;r<=faces;r++){
        int raw=pos+r; if(raw>=BOARD_SIZE) continue;
        State ns=apply_cell(raw,money,die);
        best=max(best,lookaheadScore(ns.pos,ns.money,ns.die,depth-1));
    }
    return best==INT_MIN?pos*1000+money:best;
}
int lookaheadBestRoll(int pos,int money,int die,int depth=4){
    int faces=(die==0)?6:12;
    int bestRoll=1,bestVal=INT_MIN;
    for(int r=1;r<=faces;r++){
        int raw=pos+r; if(raw>=BOARD_SIZE) continue;
        State ns=apply_cell(raw,money,die);
        int val=lookaheadScore(ns.pos,ns.money,ns.die,depth-1);
        if(val>bestVal){bestVal=val;bestRoll=r;}
    }
    return bestRoll;
}

struct Move{int roll,npos,nmoney,ndie,gval,minimax_val;bool win,skip,extra;
            string cname,cemoji,cdesc,cardname,carddesc;
            bool collected_item;int item_id;string item_name;};

vector<Move> list_moves(int pos,int money,int die,int mask=0){
    vector<Move> mv;
    int faces=(die==0)?6:12;
    for(int r=1;r<=faces;r++){
        int raw=pos+r; if(raw>BOARD_SIZE-1) continue;
        const Cell& land=BOARD[raw];
        State ns=apply_cell(raw,money,die);
        string cn="",cd=""; bool sk=false,ex=false;
        if(land.type==CARD){int idx=raw%(int)CARDS.size();
            cn=CARDS[idx].name;cd=CARDS[idx].desc;sk=CARDS[idx].skip;ex=CARDS[idx].extra;}
        if(land.type==SKIP_TURN) sk=true;
        if(land.type==EXTRA_TURN) ex=true;
        int g=ns.pos>=BOARD_SIZE-1?0:grundy(ns.pos,ns.money,ns.die);
        int mm=minimax(ns.pos,ns.money,ns.die,3,false);
        int item_idx=item_at_cell(raw);
        bool got_item=(item_idx>=0&&!((mask>>item_idx)&1));
        string item_nm=got_item?ITEMS[item_idx].name:"";
        mv.push_back({r,ns.pos,ns.money,ns.die,g,mm,(g==0),sk,ex,
                       land.name,land.emoji,land.desc,cn,cd,
                       got_item,item_idx,item_nm});
    }
    sort(mv.begin(),mv.end(),[](const Move&a,const Move&b){
        if(a.win!=b.win) return a.win>b.win; return a.npos>b.npos;});
    return mv;
}
void print_moves(const vector<Move>& mv){
    cout<<"MOVES_START\n";
    for(auto& m:mv)
        cout<<"MOVE|"<<m.roll<<"|"<<m.npos<<"|"<<m.nmoney<<"|"<<m.ndie
            <<"|"<<m.gval<<"|"<<(m.win?"WIN":"LOSS")
            <<"|"<<m.cname<<"|"<<m.cemoji<<"|"<<m.cdesc
            <<"|"<<m.cardname<<"|"<<m.carddesc
            <<"|"<<(m.skip?"1":"0")<<"|"<<(m.extra?"1":"0")
            <<"|"<<m.minimax_val
            <<"|"<<(m.collected_item?"1":"0")<<"|"<<m.item_id<<"|"<<m.item_name<<"\n";
    cout<<"MOVES_END\n";
}

void dump_bfs(){
    auto dist=bfs_min_moves();
    cout<<"BFS_START\n";
    for(int i=0;i<BOARD_SIZE;i++)
        cout<<"BFS|"<<i<<"|"<<(dist[i]==INT_MAX?-1:dist[i])<<"\n";
    cout<<"BFS_END\n";
}
void dump_dijkstra(){
    auto dist=dijkstra_min_risk();
    cout<<"DIJKSTRA_START\n";
    for(int i=0;i<BOARD_SIZE;i++)
        cout<<"DIJKSTRA|"<<i<<"|"<<(dist[i]>=1000000000?-1:dist[i])<<"\n";
    cout<<"DIJKSTRA_END\n";
}
void dump_prefix(){
    cout<<"PREFIX_START\n";
    for(int i=0;i<BOARD_SIZE;i++)
        cout<<"PREFIX|"<<i<<"|"<<prefix_query(0,i)<<"\n";
    cout<<"PREFIX_END\n";
}

void dump_algo_timings(int pos,int money,int die){
    cout<<"TIMING_START\n";
    g_memo.clear();g_vis.clear();
    auto t0=high_resolution_clock::now();
    int gv=grundy(pos,money,die);
    auto t1=high_resolution_clock::now();
    cout<<"TIMING|Grundy (Sprague-Grundy)|O(B*M*D) ≈ O(2232*faces)|"
        <<duration_cast<microseconds>(t1-t0).count()
        <<"us|G="<<gv<<"\n";

    auto t2=high_resolution_clock::now();
    int mc=binarySearchMinCoins(pos,die);
    auto t3=high_resolution_clock::now();
    cout<<"TIMING|Binary Search (min winning coins)|O(log M * B*M*D)|"
        <<duration_cast<microseconds>(t3-t2).count()
        <<"us|MinCoins="<<mc<<"\n";

    auto t4=high_resolution_clock::now();
    build_prefix_sums();
    auto t5=high_resolution_clock::now();
    int pq=prefix_query(pos,BOARD_SIZE-1);
    cout<<"TIMING|Prefix Sum (build+query)|Build O(N), Query O(1)|"
        <<duration_cast<microseconds>(t5-t4).count()
        <<"us|RangeGain["<<pos<<"-35]="<<pq<<"\n";

    auto t6=high_resolution_clock::now();
    auto dist=bfs_min_moves();
    auto t7=high_resolution_clock::now();
    int bd=dist[pos]==INT_MAX?-1:dist[pos];
    cout<<"TIMING|BFS (shortest path to finish)|O(V+E) = O("<<BOARD_SIZE<<"*12)|"
        <<duration_cast<microseconds>(t7-t6).count()
        <<"us|MinMoves="<<bd<<"\n";

    auto t8=high_resolution_clock::now();
    int mm=lookaheadBestRoll(pos,money,die,4);
    auto t9=high_resolution_clock::now();
    cout<<"TIMING|Minimax (depth=4)|O(D^4) ≈ O(20736)|"
        <<duration_cast<microseconds>(t9-t8).count()
        <<"us|BestRoll="<<mm<<"\n";

    auto t10=high_resolution_clock::now();
    auto risk=dijkstra_min_risk();
    auto t11=high_resolution_clock::now();
    int rd=risk[pos]>=1000000000?-1:risk[pos];
    cout<<"TIMING|Dijkstra (minimum-risk path)|O(E log V)|"
        <<duration_cast<microseconds>(t11-t10).count()
        <<"us|MinRisk="<<rd<<"\n";

    cout<<"TIMING_END\n";
}

void simulate2(int p1pos,int p1m,int p1d,int p2pos,int p2m,int p2d){
    cout<<"SIM_START\n";
    int turn=1,cur=1;
    bool p1sk=false,p2sk=false;
    while(turn<=MAX_TURNS){
        int pos=(cur==1)?p1pos:p2pos;
        int mon=(cur==1)?p1m:p2m;
        int die=(cur==1)?p1d:p2d;
        if(pos>=BOARD_SIZE-1) break;
        bool& mysk=(cur==1)?p1sk:p2sk;
        if(mysk){cout<<"SIM_SKIP|"<<turn<<"|"<<cur<<"\n";
            mysk=false;cur=3-cur;turn++;continue;}
        auto mv=list_moves(pos,mon,die);
        if(mv.empty()){cur=3-cur;turn++;continue;}
        const Move& b=mv[0];
        cout<<"SIM_STEP|"<<turn<<"|"<<cur
            <<"|"<<pos<<"|"<<mon<<"|"<<die<<"|"<<b.roll
            <<"|"<<b.npos<<"|"<<b.nmoney<<"|"<<b.ndie
            <<"|"<<(b.win?"WIN":"LOSS")
            <<"|"<<b.cname<<"|"<<b.cardname
            <<"|"<<(b.skip?"1":"0")<<"|"<<(b.extra?"1":"0")
            <<"|"<<b.gval<<"\n";
        if(cur==1){p1pos=b.npos;p1m=b.nmoney;p1d=b.ndie;}
        else      {p2pos=b.npos;p2m=b.nmoney;p2d=b.ndie;}
        int cp=(cur==1)?p1pos:p2pos;
        if(cp>=BOARD_SIZE-1){cout<<"SIM_WIN|"<<cur<<"|"<<turn<<"\n";break;}
        if(b.skip){bool& op=(cur==1)?p2sk:p1sk;op=true;}
        if(b.extra){turn++;continue;}
        cur=3-cur;turn++;
    }
    cout<<"SIM_END|"<<p1pos<<"|"<<p1m<<"|"<<p1d
        <<"|"<<p2pos<<"|"<<p2m<<"|"<<p2d<<"\n";
}

enum Strategy{RANDOM_AI=0,GREEDY_AI=1,MINIMAX_AI=2,GRUNDY_AI=3};
const vector<string> STRATEGY_NAMES={"Random","Greedy","Minimax","Grundy"};

int choose_roll(Strategy s,int pos,int money,int die,mt19937& rng){
    vector<Move> moves=list_moves(pos,money,die);
    if(moves.empty()) return 1;
    if(s==GRUNDY_AI) return moves[0].roll;
    if(s==MINIMAX_AI){
        const Move* best=&moves[0];
        for(const auto& m:moves)
            if(m.npos>best->npos || (m.npos==best->npos && m.minimax_val>best->minimax_val))
                best=&m;
        return best->roll;
    }
    if(s==GREEDY_AI){
        const Move* best=&moves[0];
        for(const auto& m:moves)
            if(m.npos>best->npos || (m.npos==best->npos && m.nmoney>best->nmoney))
                best=&m;
        return best->roll;
    }
    uniform_int_distribution<int> pick(0,(int)moves.size()-1);
    return moves[pick(rng)].roll;
}

struct MatchResult{int winner,turns,p1money,p2money;};
MatchResult play_match(Strategy s1,Strategy s2,mt19937& rng){
    int p1pos=0,p2pos=0,p1m=INITIAL_MONEY,p2m=INITIAL_MONEY,p1d=0,p2d=0;
    bool p1sk=false,p2sk=false;
    int cur=1;
    for(int turn=1;turn<=MAX_TURNS;turn++){
        int& pos=(cur==1)?p1pos:p2pos;
        int& money=(cur==1)?p1m:p2m;
        int& die=(cur==1)?p1d:p2d;
        bool& skip=(cur==1)?p1sk:p2sk;
        if(pos>=BOARD_SIZE-1) return {cur,turn,p1m,p2m};
        if(skip){skip=false;cur=3-cur;continue;}
        int roll=choose_roll((cur==1)?s1:s2,pos,money,die,rng);
        int raw=pos+roll;
        if(raw<=BOARD_SIZE-1){
            State ns=apply_cell(raw,money,die);
            const Cell& c=BOARD[raw];
            bool sk=(c.type==SKIP_TURN),ex=(c.type==EXTRA_TURN);
            if(c.type==CARD){int idx=raw%(int)CARDS.size();sk=CARDS[idx].skip;ex=CARDS[idx].extra;}
            pos=ns.pos; money=ns.money; die=ns.die;
            if(pos>=BOARD_SIZE-1) return {cur,turn,p1m,p2m};
            if(sk){bool& opp=(cur==1)?p2sk:p1sk;opp=true;}
            if(ex) continue;
        }
        cur=3-cur;
    }
    if(p1pos!=p2pos) return {p1pos>p2pos?1:2,MAX_TURNS,p1m,p2m};
    return {p1m>=p2m?1:2,MAX_TURNS,p1m,p2m};
}

void dump_tournament(){
    const int N=STRATEGY_NAMES.size(), ROUNDS=20;
    vector<int> wins(N,0), games(N,0), turns_sum(N,0), money_sum(N,0);
    mt19937 rng(42);
    for(int a=0;a<N;a++){
        for(int b=0;b<N;b++){
            if(a==b) continue;
            for(int r=0;r<ROUNDS;r++){
                MatchResult res=play_match((Strategy)a,(Strategy)b,rng);
                games[a]++; games[b]++;
                turns_sum[a]+=res.turns; turns_sum[b]+=res.turns;
                money_sum[a]+=res.p1money; money_sum[b]+=res.p2money;
                if(res.winner==1) wins[a]++; else wins[b]++;
            }
        }
    }
    cout<<"TOURNAMENT_START\n";
    for(int i=0;i<N;i++){
        double win_rate=games[i]?100.0*wins[i]/games[i]:0.0;
        double avg_turns=games[i]?1.0*turns_sum[i]/games[i]:0.0;
        double avg_money=games[i]?1.0*money_sum[i]/games[i]:0.0;
        cout<<"TOURNAMENT|"<<STRATEGY_NAMES[i]<<"|"<<wins[i]<<"|"<<games[i]
            <<"|"<<fixed<<setprecision(1)<<win_rate
            <<"|"<<avg_turns<<"|"<<avg_money<<"\n";
    }
    cout<<"TOURNAMENT_END\n";
}

void dump_cells(){
    cout<<"CELLS_START\n";
    for(int i=0;i<BOARD_SIZE;i++){
        auto& c=BOARD[i];
        cout<<"CELL|"<<c.id<<"|"<<(int)c.type<<"|"<<c.value
            <<"|"<<c.emoji<<"|"<<c.name<<"|"<<c.desc<<"\n";
    }
    cout<<"CELLS_END\n";
}
void dump_graph(){
    cout<<"GRAPH_START\n";
    for(int i=0;i<BOARD_SIZE-1;i++) cout<<"EDGE|"<<i<<"|"<<(i+1)<<"|normal\n";
    vector<tuple<int,int,string>> sp={
        {4,8,"Quick Ride"},{16,13,"Missed Bus"},{23,26,"Fast Track"},
        {31,27,"Rain"},{13,16,"Card-WP"},{24,21,"Card-WP2"},
        {33,30,"Card-SC"},{18,20,"Lucky+skip"}};
    for(const auto& e:sp)
        cout<<"EDGE|"<<get<0>(e)<<"|"<<get<1>(e)<<"|"<<get<2>(e)<<"\n";
    cout<<"GRAPH_END\n";
}

int main(int argc,char* argv[]){
    ios::sync_with_stdio(false); cin.tie(nullptr);
    build_prefix_sums();
    if(argc<2){cerr<<"Usage: engine <mode>\n";return 1;}
    string mode=argv[1];
    if(mode=="cellinfo"){dump_cells();return 0;}
    if(mode=="graph"){dump_graph();return 0;}
    if(mode=="bfs"){dump_bfs();return 0;}
    if(mode=="dijkstra"){dump_dijkstra();return 0;}
    if(mode=="prefix"){dump_prefix();return 0;}
    if(mode=="tournament"){dump_tournament();return 0;}
    if(mode=="simulate"){
        int p1p=0,p1m=INITIAL_MONEY,p1d=0,p2p=0,p2m=INITIAL_MONEY,p2d=0;
        cin>>p1p>>p1m>>p1d>>p2p>>p2m>>p2d;
        simulate2(p1p,p1m,p1d,p2p,p2m,p2d);
        return 0;
    }
    int pos=0,money=INITIAL_MONEY,die=0;
    cin>>pos>>money>>die;
    money=min(money,MAX_MONEY);
    if(mode=="timings"){dump_algo_timings(pos,money,die);return 0;}
    if(mode=="binsearch"){
        cout<<"BINSEARCH|"<<binarySearchMinCoins(pos,die)<<"\n";
        return 0;
    }
    if(mode=="grundy"){
        int g=grundy(pos,money,die);
        cout<<"GRUNDY|"<<g<<"\n";
        cout<<"STATE|"<<(g!=0?"WINNING":"LOSING")<<"\n";
        print_moves(list_moves(pos,money,die,0));
    } else if(mode=="moves"){
        print_moves(list_moves(pos,money,die,0));
    } else if(mode=="apply"){
        int roll; cin>>roll;
        int raw=pos+roll;
        if(raw>BOARD_SIZE-1){cout<<"INVALID|overshoot\n";}
        else{
            State ns=apply_cell(raw,money,die);
            const Cell& c=BOARD[raw];
            bool sk=(c.type==SKIP_TURN),ex=(c.type==EXTRA_TURN);
            string cn="",cd="";
            if(c.type==CARD){int idx=raw%(int)CARDS.size();
                cn=CARDS[idx].name;cd=CARDS[idx].desc;sk=CARDS[idx].skip;ex=CARDS[idx].extra;}
            int item_idx=item_at_cell(raw);
            string item_nm=(item_idx>=0)?ITEMS[item_idx].name:"";
            cout<<"RESULT|"<<ns.pos<<"|"<<ns.money<<"|"<<ns.die
                <<"|"<<c.emoji<<" "<<c.name<<"|"<<c.desc
                <<"|"<<cn<<"|"<<cd
                <<"|"<<(sk?"1":"0")<<"|"<<(ex?"1":"0")
                <<"|"<<item_nm<<"\n";
        }
    }
    return 0;
}
