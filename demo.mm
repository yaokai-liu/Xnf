machine x64 {
  register gax [64-bit] {
    rax: [63-0] = 0x00;
    eax: [31-0] = 0x00;
    ax : [15-0] = 0x00;
    ah : [15-8] = 0x04;
    al : [7-0]  = 0x00;
  };
  register gbx [64-bit] {
    rbx: [63-0] = 0x00;
    ebx: [31-0] = 0x00;
    bx : [15-0] = 0x00;
    bh : [15-8] = 0x04;
    bl : [7-0]  = 0x00;
  };
  immediate refer [23-bit] unsigned;
  memory local [12-bit] {
    $: [6-11];
    >: [0-5];
  };
  memory far [24-bit] {
    $: [13-24];
    >: [0-12];
  };
  set gpr {gax, gbx};
  instruction mov {
    [gpr g, local l] = [10-byte] (4-tick) {
      ^ : [8] = 0x56;
      & : [8] = 0x37;
      ~ : [64] = {
        [0-5] = l.$,
        [63-56] = g,
        [16-11] = l.>,
        [23-31] = g,
        [...] = 0
      };
    };
    [gax g, local l, far f] = [10-byte] (4-tick) {
      ^ : [8] = 0x56;
      & : [8] = 0x37;
      ~ : [64] = {
        [0-5] = l.$,
        [63-56] = g,
        [16-11] = l.>,
        [23-31] = g,
        [...] = 0
      };
    };
    [local l, gax g, far f] = [10-byte] (4-tick) {
      ^ : [8] = 0x56;
      & : [8] = 0x37;
      ~ : [64] = {
        [0-5] = l.$,
        [63-56] = g,
        [16-11] = l.>,
        [23-31] = g,
        [...] = 0
      };
    };
  };
  instruction mattv {
      [] = [1-byte] {
        ~: [8] = 0x20;
    };
  };
};
