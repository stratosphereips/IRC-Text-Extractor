module IRC;

type IRC_Event: record {
    ts: time;
    src: string;
    src_ip: addr;
    src_port: port;
    dst: string;
    dst_ip: addr;
    dst_port: port;
    msg: string &optional; 
    msg_size: int &optional; 
};

type IRC_Session: record {
    src: string;
    src_ip: addr;
    src_port: port;
    dst: string;
    dst_ip: addr;
    dst_port: port;
    start_time: time;
    end_time: time;
    duration: int;
    msg_count: count;
    pkt_size_total: int;
    periodicity: int &optional;
    spec_chars_username_mean: double;
    spec_chars_msg_mean: double;
    msg_word_entropy: double;
    # malicious: bool;
    msgs: vector of IRC_Event;
};

type IRC_EventKey: record {
    src_ip: addr;
    dst_ip: addr;
    dst_port: port;
};

type Complex: record {
    real: double;
    imag: double;
};

type event_vec: vector of IRC_Event;
type double_vec: vector of double;

global irc_logs: vector of IRC_Event;

event zeek_init()
{
    print "zeek init";
}

event irc_log(rec: IRC::Info) {
    if (rec$command != "USER") return;
    local ev: IRC_Event = IRC_Event($ts=rec$ts, $src=rec$user, $src_ip=rec$id$orig_h, $src_port=rec$id$orig_p, $dst="", $dst_ip=rec$id$resp_h, $dst_port=rec$id$resp_p, $msg=rec$addl);
    irc_logs += ev;
}

global organize_events: function(): vector of event_vec;
global extract_sessions: function();
global mean_f: function(x:vector of double): double;
global sum_f: function(x:vector of double): double;
global ln_f: function(x:vector of double): vector of double;
global fft: function(x: vector of Complex): vector of Complex;
global compute_session_periodicity: function(ts_vec: vector of time): double;
global slice_c: function(x: vector of Complex, start: int, step:int): vector of Complex;
global mult_cc: function(a:Complex, b:Complex): Complex;
global mult_cd: function(a:Complex, b:double): Complex;
global exp_c: function(c: Complex): Complex;
global sin: function(x: double): double;
global cos: function(x: double): double;
global cosh: function(x: double): double ;
global sinh: function(x: double): double ;
global pow: function(x:double, p:int): double;
global add_cc: function(a: Complex, b: Complex): Complex;
global sub_cc: function(a: Complex, b:Complex): Complex;
global fft_preprocess_seq: function(x: vector of Complex): vector of Complex;

event zeek_done()
{
    extract_sessions();
}

local irc_sessions: vector of IRC_Session;
### FUNCTION HEADERS 
# COMPLEX
local add_cd: function(a: Complex, b: double): Complex;
local div_cc: function(a:Complex, b:Complex): Complex;
local div_cd: function(a:Complex, b:double): Complex;
# UTILS
# MAIN
local get_key: function(ev: IRC_Event): IRC_EventKey;
local extract_features: function(out:file);


### FUNCTION IMPLEMENTATION
extract_sessions = function()
{
    print "extract sessions...";
    local events: vector of event_vec = organize_events();
    for (i in events) {
        local ev: IRC_Event = events[i][0];
        local src: string = ev$src;
        local src_ip: addr = ev$src_ip;
        local start_time: time = ev$ts;
        local dst: string = ev$dst;
        local dst_ip: addr = ev$dst_ip;
        local dst_port: port = ev$dst_port;

        local packet_size_total: int;
        local msg_ts_vec: vector of time;
        local msg_count: count = |events[i]|;
        local word_occurency_table: table[string] of count;

        local _spec_chars_username_rgx: PatternMatchResult = match_pattern(src, /[^A-Za-z]/);
        local spec_chars_username_mean: double = |_spec_chars_username_rgx$str| / |src|;
        local msg_special_chars: vector of double;

        for (j in events[i])
        {
            local ev2: IRC_Event = events[i][j];
            msg_ts_vec += ev2$ts;
            local msg: string = ev2$msg;
            local split_msg: string_vec = split_string(msg,/ /);
            
            # compute word occurency
            for (k in split_msg) {
                local w: string = split_msg[k];
                if (w in word_occurency_table) {
                    word_occurency_table[w] += 1;
                } else {
                    word_occurency_table[w] = 1;
                }
            }

            # compute msg special chars
            local _msg_spec_rgx: PatternMatchResult = match_pattern(msg, /[^A-Za-z]/);
            local msg_spec: double = |_msg_spec_rgx$str| / |msg|;
            msg_special_chars += msg_spec;

            
        }

        # compute msg word entropy
        local word_count_sum: count = 0;
        local word_count: count = |word_occurency_table|;
        local p: vector of double;

        local c: count;
        local word: string;
        for (word, c in word_occurency_table)
        {
            p += c;
            word_count_sum += c;
        }
        p = p / word_count_sum;

        # compute msg special chars mean
        local spec_chars_msg_mean: double = mean_f(msg_special_chars);    
        local msg_word_entropy: double = -sum_f(p * (ln_f(p)/ln(2)));

        local per: double = compute_session_periodicity(msg_ts_vec);
        #TODO: implement
        #local per_max: count = most_prob_per(per)
        #local data_splitted: vector of double_vec  = split_by_period(per_max);
        #local per_nmse: double = compute_nmse(data_splitted);
        
        # local session: IRC_Session = IRC_Session()
    }

};

organize_events = function(): vector of event_vec
{
    print "organize events...";
    local sessions:vector of event_vec;
    for (i in irc_logs) {
        local el1: IRC_Event = irc_logs[i];
        # create a session and for loop the rest of the logs and add which is matching by the key  and create 'array of arrays'
        local session_vec: event_vec;
        session_vec += el1;
        # local el_key = get_key(el);
        for (j in irc_logs)
        {
            if (i == j) next;
            local el2: IRC_Event = irc_logs[j]; 
            if (el1$src_ip == el2$src_ip && el1$dst_ip == el2$dst_ip && el1$dst_port == el2$dst_port ) session_vec += el2;
        }
        sessions += session_vec;
    }
    return sessions;
};

compute_session_periodicity = function(ts_vec: vector of time): double
{
    print "compute_session_periodicity...";
    local ts_vecsize: count = |ts_vec|;
    local time_diff_vec: vector of double; 
    local td_vec: vector of double;
    local td_vec_c: vector of Complex;
    for (i in ts_vec)
    {
        if (i+1 == ts_vecsize) break;
        local td: double = interval_to_double(ts_vec[i+1] - ts_vec[i]);
        td_vec += td;
        td_vec_c += Complex($real=td, $imag=0);
    }

    if (|td_vec_c| > 0) {
        print |td_vec_c|;
        local td_vec_c2: vector of Complex = fft_preprocess_seq(td_vec_c);
        print |td_vec_c2|;
        print "fft...";
        local per_vec: vector of Complex = fft(td_vec_c2);
    }

    local per_vec_real: vector of double;

    for (i in per_vec)
    {
        per_vec_real += per_vec[i]$real;
    }

    local m_per: double = mean_f(per_vec_real);
    print m_per;
    return m_per;
};


# fast fourier transform
fft = function(x: vector of Complex): vector of Complex 
{
    # print "fft..";
    local N: count = |x|;
    if (N <= 1) return x;
    local x_odd: vector of Complex = slice_c(x, 0, 2);
    local x_even: vector of Complex = slice_c(x, 1, 2);
    local fft_even: vector of Complex = fft(x_even);
    local fft_odd: vector of Complex = fft(x_odd);

    local T_vec: vector of Complex;
    local nn: int =  N/2;
    local pi: double = 3.14159265;
    local c: Complex = Complex($real=0, $imag=-2);
    local k: int = 0;
    
    while (k != nn)
    {
        local tmp_d: double = pi * k/N;
        local c2: Complex = mult_cd(c, tmp_d);
        local c3: Complex = exp_c(c2);
        T_vec += mult_cc(c3,fft_odd[k]);
        k += 1;
    }

    local res: vector of Complex;
    local k2: count = 0;
    while (k2 != nn)
    {
        res += add_cc(fft_even[k2], T_vec[k2]);
        k2 += 1; 
    }
    
    local k3: count = 0;
    while (k3 != nn)
    {
        res += sub_cc(fft_even[k3], T_vec[k3]);
        k3 += 1;
    }

    return res;
};

# # Extract features to the file
# extract_features = function(out:file)
# {
#     print "extract_features...";
#     # TODO
# };


# get_key = function(ev: IRC_Event): IRC_EventKey
# {
#     print "get_key...";
#     local ev_key: IRC_EventKey = IRC_EventKey($src_ip=ev$src_ip, $dst_ip=ev$dst_ip, $dst_port=ev$dst_port);
#     return ev_key;
# };

fft_preprocess_seq = function(x: vector of Complex): vector of Complex 
{

    local x_len: int = |x|;
    local x_new: vector of Complex;
    local x_pow: int = ln(x_len)/ln(2);
    local x_len_new : double = pow(2,x_pow);
    local i: count = 0;
    while (i < x_len_new) 
    {
        x_new += x[i];
        i += 1;
    }
    return x_new;
};

# ## COMPLEX 
add_cc = function(a: Complex, b: Complex): Complex
{
    # print "add_cc";
    local r: double = a$real + b$real;
    local i: double = a$imag + b$imag;
    local c: Complex = Complex($real=r, $imag=i);
    return c;
};

sub_cc = function(a: Complex, b:Complex): Complex
{
    # print "sub_cc";
    local r: double = a$real - b$real;
    local i: double = a$imag - b$imag;
    local c: Complex = Complex($real=r, $imag=i);
    return c;
};

mult_cc = function(a:Complex, b:Complex): Complex
{
    # print "mult_cc";
    local r: double = a$real * b$real - a$imag * b$imag;
    local i: double = a$imag * b$real + a$real * b$imag;
    local c: Complex = Complex($real=r, $imag=i);
    return c;
};

mult_cd = function(a:Complex, b:double): Complex
{
    # print "mult_cd";
    local r: double = a$real * b;
    local i: double = a$imag *b;
    local c: Complex = Complex($real=r, $imag=i);
    return c;
};

cosh = function(x: double): double
{
    # print "cosh";
    local r: double = (exp(x) + exp(-x))/2;
    return r;
};

sinh = function(x: double): double
{
    # print "sinh";
    local r: double = (exp(x) - exp(-x))/2;
    return r;
};

sin = function(x: double): double
{
    # print "sin";
    local a: double = x;
    local s: double = a;
    local i:count = 1;
    while (i != 100) {
        local a_c: double =  -1 * pow(x,2);
        local a_j: double  = (2 * i) * (2 * i + 1);
        a = a * (a_c / a_j);
        s += a;
        i += 1;
    }
    return s;
};

cos = function(x: double): double
{
    # print "cos";
    local offset: double = 3.14159265/2.0;
    return sin(x+offset);
};

exp_c = function(c: Complex) : Complex
{
    # print "exp_C";
    local r: double = cosh(c$real) + sinh(c$real);
    local imcos: double = cos(c$imag);
    local imsin: double = sin(c$imag);
    local cc: Complex = Complex($real=imcos, $imag=imsin);
    local cc2: Complex = mult_cd(cc, r);
    return cc2;
};

# # assumptions: step > 0, |x| >= start >= 0,  end = |x|
# # TODO: test the correctness
slice_c = function(x: vector of Complex, start: int, step:int): vector of Complex
{
    # print "slice_c";
    local slice_x: vector of Complex;
    for (i in x) {
        if (i >= start && (i-start) % step == 0) {
            slice_x += x[i];
        }
    }
    return slice_x;
};
# ## UTILS
pow = function(x:double, p:int) : double
{
    # print "pow";
    local x_p: double = x;
    local i: count = 0;
    while (i != p-1)
    {
        x_p = x_p*x;
        i += 1;
    }
    return x_p;
};

sum_f = function(x:vector of double): double
{
    # print "add_cc";
    local sum_r: double = 0;
    for (i in x)
    {
        sum_r += x[i];
    }
    return sum_r;
};

mean_f = function(x:vector of double): double
{
    # print "mean_f...";
    local mm: double = sum_f(x)/ |x|;
    return mm;
};

ln_f = function(x:vector of double): vector of double
{
    # print "ln_f";
    local ln_vec: vector of double;
    for (i in x) {
        ln_vec += ln(x[i]);
    }
    return ln_vec;
};