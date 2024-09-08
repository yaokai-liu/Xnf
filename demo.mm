machine x64 {
  register ax [64-bits] {
    r~ : [63-0] = 0x00;
    e~ : [31-0] = 0x00;
    ~  : [15-0] = 0x00;
    ah : [15-8] = 0x04;
    al : [7-0]  = 0x00;
  };
  immediate refer [23-bit] unsigned;
  memory local [12-bit] {
    >: [6-11];
    $: [0-5];
  };
  instruction mov {
    [ax, local] = [10-byte] (4-tick) {
      ^ : [8] = 0x56;
      & : [8] = 0x37;
      ~ : [64] = {
        [0-5] = local.$,
        [63-56] = ax,
        [22-11] = local.>,
        [...] = 0
      };
    };
  };
};
