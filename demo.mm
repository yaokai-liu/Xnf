machine x64 {
  register gax [64-bit] {
    rax: [63-0] = 0x00;
    eax: [31-0] = 0x00;
    ax : [15-0] = 0x00;
    ah : [15-8] = 0x04;
    al : [7-0]  = 0x00;
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
  instruction mov {
    [gax, local] = [10-byte] (4-tick) {
      ^ : [8] = 0x56;
      & : [8] = 0x37;
      ~ : [64] = {
        [0-5] = local.$,
        [63-56] = gax,
        [16-11] = local.>,
        [23-31] = gax,
        [...] = 0
      };
    };
  };
};
