import niscope
import nifgen
import nisync
import numpy as np
from nisync.constants import CLK_OUT, OSCILLATOR, CLK_IN, PXI_CLK10_IN, PXI_TRIG0, PFI0
import matplotlib.pyplot as plt

# --- Hardware Configuration Resources ---
MASTER_SCOPE = "PXI1_SCOPE1"
REST_SCOPES = ["PXI2_SCOPE2"]
MASTER_SYNC = "PXI1_MasterSync"
REST_SYNC = "PXI2_RestSync"
FGEN = "PXI1_FGEN1"

# --- Scope & FGEN Settings ---
CHANNEL = "0"
SAMPLE_RATE = 100e6
RECORD_LENGTH = 100_000
VERTICAL_RANGE = 2.0
VERTICAL_OFFSET = 0.0
TRIGGER_LEVEL = 0.5
REFERENCE_POSITION = 50.0

# --- Trigger & Routing Settings ---
MASTER_SCOPE_REF_TRIGGER_EXPORT = PXI_TRIG0
MASTER_SYNC_REF_TRIGGER_EXPORT = PFI0
REST_SYNC_REF_TRIGGER_IMPORT = PFI0
REST_SCOPE_REF_TRIGGER_IMPORT = PXI_TRIG0

# --- Helper Functions ---
def build_list_of_scopes():
    scope_list = []
    scope_list.append(MASTER_SCOPE)
    for REST_SCOPE in REST_SCOPES:
        scope_list.append(REST_SCOPE)
    return scope_list

def configure_scope(scope, is_master):
    # --- Configure the scope range ---
    print(f"Configuring: {scope.io_resource_descriptor} as Master: {is_master}")
    scope.configure_vertical(
        range=VERTICAL_RANGE,
        coupling=niscope.VerticalCoupling.DC,
        offset=VERTICAL_OFFSET,
        probe_attenuation=1.0,
        enabled=True
    )

    # --- Configure the scope timing / acquisition ---
    scope.configure_horizontal_timing(
        min_sample_rate=SAMPLE_RATE,
        min_num_pts=RECORD_LENGTH,
        ref_position=REFERENCE_POSITION,
        num_records=1,
        enforce_realtime=True
    )

    if is_master:
        # --- Configure the scope master reference trigger for analog edge and export trigger to PXI trig lines ---
        scope.configure_trigger_edge(
            trigger_source=CHANNEL,
            level=TRIGGER_LEVEL,
            trigger_coupling=niscope.TriggerCoupling.DC,
            slope=niscope.enums.TriggerSlope.POSITIVE
        )
        scope.exported_ref_trigger_output_terminal = MASTER_SCOPE_REF_TRIGGER_EXPORT

    else:
        # --- Configure the remaining scope reference trigger for digital edge coming from PXI trig lines ---
        scope.configure_trigger_digital(
            trigger_source = REST_SCOPE_REF_TRIGGER_IMPORT,
            slope=niscope.enums.TriggerSlope.POSITIVE
        )

def configure_fgen(fgen):
    # --- Configure the FGEN to output a Square wave to use for edge detection ---
    print(f"Configuring: {fgen.io_resource_descriptor}")
    fgen.output_mode = nifgen.OutputMode.FUNC   # Select "standard function" mode
    fgen.channels[CHANNEL].configure_standard_waveform(
        waveform=nifgen.Waveform.SQUARE,
        amplitude=TRIGGER_LEVEL*2,           # V pk-pk
        frequency=10_000,           # Hz
        dc_offset=0.0,               # V
        start_phase=0.0
    )              # degrees

def find_threshold_crossing(array, threshold, direction="rising"):
    # --- Determine the first threshold crossing in an array, then interpolate to find the decimal sample ---
    arr = np.asarray(array, dtype=float)
    shifted = arr - threshold
    if direction == "rising":
        mask = (shifted[:-1] < 0) & (shifted[1:] >= 0)
    elif direction == "falling":
        mask = (shifted[:-1] >= 0) & (shifted[1:] < 0)
    else:  # both
        mask = np.diff(np.signbit(shifted))
    indices = np.where(mask)[0]
    if len(indices) == 0:
        return None
    i = indices[0]
    fraction = (threshold - arr[i]) / (arr[i + 1] - arr[i])
    return i + fraction

def fetch_and_compare_waveforms(master_scope, rest_scopes):
    # --- Build an array of fetched data from the scopes, find the decimal threshold crossing, and return values ---
    samples_array = []

    # --- Scope Fetch on Master ---
    wfm_master = master_scope.channels[CHANNEL].fetch(num_samples=RECORD_LENGTH)[0]

    # --- Find master sample offset ---
    master_samples = np.asarray(wfm_master.samples, dtype=float)
    samples_array.append(master_samples)
    master_index_crossing = find_threshold_crossing(master_samples, TRIGGER_LEVEL)

    # --- Scope Fetch on Rest ---
    rest_index_crossing_array = []
    for rest_scope in rest_scopes:
        wfm_rest = rest_scope.channels[CHANNEL].fetch(num_samples=RECORD_LENGTH)[0]
        # --- Find rest sample offset ---
        rest_samples = np.asarray(wfm_rest.samples, dtype=float)
        samples_array.append(rest_samples)
        rest_index_crossing_array.append(find_threshold_crossing(rest_samples, TRIGGER_LEVEL))

    # --- Calculated worst case offset with respect to master ---
    sample_offset_all = master_index_crossing - rest_index_crossing_array
    if max(abs(sample_offset_all)) > min(abs(sample_offset_all)):
        sample_offset= max(sample_offset_all)
    else:
        sample_offset = min(sample_offset_all)

    # --- Convert sample offset to time ---
    time_offset = sample_offset * (1/SAMPLE_RATE)

    return samples_array, sample_offset, time_offset

def switch_clock_signals(connect):
    if connect:
        # --- Connect the clocks ---
        master_sync.connect_clock_terminals(OSCILLATOR, CLK_OUT)
        master_sync.connect_clock_terminals(CLK_IN, PXI_CLK10_IN)
        rest_sync.connect_clock_terminals(CLK_IN, PXI_CLK10_IN)

    else:
        # --- Disconnect the clocks ---
        master_sync.disconnect_clock_terminals(OSCILLATOR, CLK_OUT)
        master_sync.disconnect_clock_terminals(CLK_IN, PXI_CLK10_IN)
        rest_sync.disconnect_clock_terminals(CLK_IN, PXI_CLK10_IN)

def switch_ref_triggers(connect):
    if connect:
        # --- Connect Reference Trigger ---
        master_sync.connect_trigger_terminals(MASTER_SCOPE_REF_TRIGGER_EXPORT, MASTER_SYNC_REF_TRIGGER_EXPORT)
        rest_sync.connect_trigger_terminals(REST_SYNC_REF_TRIGGER_IMPORT, REST_SCOPE_REF_TRIGGER_IMPORT)
    else:
        # --- Disconnect Reference Trigger ---
        master_sync.disconnect_trigger_terminals(MASTER_SCOPE_REF_TRIGGER_EXPORT, MASTER_SYNC_REF_TRIGGER_EXPORT)
        rest_sync.disconnect_trigger_terminals(REST_SYNC_REF_TRIGGER_IMPORT, REST_SCOPE_REF_TRIGGER_IMPORT)

# --- Main Sequence ---
with nisync.Session(MASTER_SYNC) as master_sync, nisync.Session(REST_SYNC) as rest_sync:
    # --- Build a list of all scopes ---
    scope_resources = build_list_of_scopes()

    # --- Generate Clock from Master Chassis and Connect it to Rest of Chassis ---
    switch_clock_signals(connect=True)

    # --- Connect Ref Trigger from Master Chassis to Rest of Chassis ---
    switch_ref_triggers(connect=True)

    # --- Create FGEN session ---
    with nifgen.Session(FGEN) as fgen:

        # --- Create Master Scope session ---
        with niscope.Session(MASTER_SCOPE) as master_scope:
            # --- Create Rest of Scopes sessions ---
            rest_scopes = [niscope.Session(rest_scope) for rest_scope in REST_SCOPES]

            # --- Configure Master Scope ---
            configure_scope(master_scope, is_master=True)

            # --- Configure Rest of Scopes ---
            for rest_scope in rest_scopes:
                configure_scope(rest_scope, is_master=False)

            # --- Configure FGEN session ---
            configure_fgen(fgen)

            # --- Start the rest of the scopes first as they wait on the refer trigger from master, then start master scope ---
            for rest_scope in rest_scopes:
                rest_scope.initiate()
            master_scope.initiate()
            print("Waiting: Scopes waiting for reference trigger")

            # --- Start square wave, should trigger master, which should trigger rest of scopes ---
            fgen.initiate()
            print(f"Generating: {fgen.io_resource_descriptor} is generating")

            # --- Fetch triggered data, calcuate offsets ---
            fetched_samples_array, calculated_sample_offset, calculated_time_offset = fetch_and_compare_waveforms(master_scope, rest_scopes)

            # --- Stop generating square wave ---
            fgen.abort()

            # --- Stop scopes (Master will stop automatically) ---
            for rest_scope in rest_scopes:
                rest_scope.abort()
                rest_scope.close()

    # --- Disconnect the Ref Trigger ---
    switch_ref_triggers(connect=False)

    # --- Disconnect the Clock ---
    switch_clock_signals(connect=False)

    # --- Print Results ---
    print(f"Result: Sample Offset: {calculated_sample_offset}")
    print(f"Result: Time Offset (sec): {calculated_time_offset:.9f} s")
    print(f"Result: Time Offset (nsec): {calculated_time_offset * 1_000_000_000:.6f} ns")

    # --- Plot Results ---
    plt.figure()
    for  scope_resource in scope_resources:
        plt.plot(fetched_samples_array[scope_resources.index(scope_resource)], label=f"{scope_resources[scope_resources.index(scope_resource)]}")
    plt.title(f"Scope Trace")
    plt.legend()
    plt.show()