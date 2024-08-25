machine x64 {
    register ax [64 bit] {
        r~ : [63-0] = 0;
        e~ : [31-0] = 1;
        ~  : [15-0] = 2;
        !ah : [15-8] = 4;
        !al : [7-0] = 8;
    };
    immediate refer [23 bit] unsigned;
    memory local [12 bit] {
        >: [6-11];
        $: [0-5];
    };
    instruction mov {
        [ax, local] = [12 byte]  4  {
            ^ : [8] = 0x56;
            & : [8] = 0x37;
            ~ : [64] = {
                [0-5] = local.base,
                [63-56] = $ax,
                [22-11] = local.offset,
                [...] = 0
            };
        };
    }
};
