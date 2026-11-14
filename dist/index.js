const manifest = {"name":"Arcoon Deck"};
const API_VERSION = 2;
const internalAPIConnection = window.__DECKY_SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED_deckyLoaderAPIInit;
if (!internalAPIConnection) {
    throw new Error('[@decky/api]: Failed to connect to the loader as as the loader API was not initialized. This is likely a bug in Decky Loader.');
}
let api;
try {
    api = internalAPIConnection.connect(API_VERSION, manifest.name);
}
catch {
    api = internalAPIConnection.connect(1, manifest.name);
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version 1. Some features may not work.`);
}
if (api._version != API_VERSION) {
    console.warn(`[@decky/api] Requested API version ${API_VERSION} but the running loader only supports version ${api._version}. Some features may not work.`);
}
const callable = api.callable;
const addEventListener = api.addEventListener;
const removeEventListener = api.removeEventListener;
const routerHook = api.routerHook;
const toaster = api.toaster;
const definePlugin = (fn) => {
    return (...args) => {
        return fn(...args);
    };
};

const PLUGIN_NAME = "Arcoon Deck";
function showToast(body, options) {
    return toaster.toast({ title: PLUGIN_NAME, body, ...options });
}

var DefaultContext = {
  color: undefined,
  size: undefined,
  className: undefined,
  style: undefined,
  attr: undefined
};
var IconContext = SP_REACT.createContext && /*#__PURE__*/SP_REACT.createContext(DefaultContext);

var _excluded = ["attr", "size", "title"];
function _objectWithoutProperties(e, t) { if (null == e) return {}; var o, r, i = _objectWithoutPropertiesLoose(e, t); if (Object.getOwnPropertySymbols) { var n = Object.getOwnPropertySymbols(e); for (r = 0; r < n.length; r++) o = n[r], -1 === t.indexOf(o) && {}.propertyIsEnumerable.call(e, o) && (i[o] = e[o]); } return i; }
function _objectWithoutPropertiesLoose(r, e) { if (null == r) return {}; var t = {}; for (var n in r) if ({}.hasOwnProperty.call(r, n)) { if (-1 !== e.indexOf(n)) continue; t[n] = r[n]; } return t; }
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), true).forEach(function (r) { _defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function _defineProperty(e, r, t) { return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: true, configurable: true, writable: true }) : e[r] = t, e; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == typeof i ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != typeof t || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r); if ("object" != typeof i) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
function Tree2Element(tree) {
  return tree && tree.map((node, i) => /*#__PURE__*/SP_REACT.createElement(node.tag, _objectSpread({
    key: i
  }, node.attr), Tree2Element(node.child)));
}
function GenIcon(data) {
  return props => /*#__PURE__*/SP_REACT.createElement(IconBase, _extends({
    attr: _objectSpread({}, data.attr)
  }, props), Tree2Element(data.child));
}
function IconBase(props) {
  var elem = conf => {
    var attr = props.attr,
      size = props.size,
      title = props.title,
      svgProps = _objectWithoutProperties(props, _excluded);
    var computedSize = size || conf.size || "1em";
    var className;
    if (conf.className) className = conf.className;
    if (props.className) className = (className ? className + " " : "") + props.className;
    return /*#__PURE__*/SP_REACT.createElement("svg", _extends({
      stroke: "currentColor",
      fill: "currentColor",
      strokeWidth: "0"
    }, conf.attr, attr, svgProps, {
      className: className,
      style: _objectSpread(_objectSpread({
        color: props.color || conf.color
      }, conf.style), props.style),
      height: computedSize,
      width: computedSize,
      xmlns: "http://www.w3.org/2000/svg"
    }), title && /*#__PURE__*/SP_REACT.createElement("title", null, title), props.children);
  };
  return IconContext !== undefined ? /*#__PURE__*/SP_REACT.createElement(IconContext.Consumer, null, conf => elem(conf)) : elem(DefaultContext);
}

// THIS FILE IS AUTO GENERATED
function FaTrash (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M432 32H312l-9.4-18.7A24 24 0 0 0 281.1 0H166.8a23.72 23.72 0 0 0-21.4 13.3L136 32H16A16 16 0 0 0 0 48v32a16 16 0 0 0 16 16h416a16 16 0 0 0 16-16V48a16 16 0 0 0-16-16zM53.2 467a48 48 0 0 0 47.9 45h245.8a48 48 0 0 0 47.9-45L416 128H32z"},"child":[]}]})(props);
}function FaTimesCircle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8zm121.6 313.1c4.7 4.7 4.7 12.3 0 17L338 377.6c-4.7 4.7-12.3 4.7-17 0L256 312l-65.1 65.6c-4.7 4.7-12.3 4.7-17 0L134.4 338c-4.7-4.7-4.7-12.3 0-17l65.6-65-65.6-65.1c-4.7-4.7-4.7-12.3 0-17l39.6-39.6c4.7-4.7 12.3-4.7 17 0l65 65.7 65.1-65.6c4.7-4.7 12.3-4.7 17 0l39.6 39.6c4.7 4.7 4.7 12.3 0 17L312 256l65.6 65.1z"},"child":[]}]})(props);
}function FaMicrochip (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M416 48v416c0 26.51-21.49 48-48 48H144c-26.51 0-48-21.49-48-48V48c0-26.51 21.49-48 48-48h224c26.51 0 48 21.49 48 48zm96 58v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42V88h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zm0 96v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42v-48h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zm0 96v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42v-48h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zm0 96v12a6 6 0 0 1-6 6h-18v6a6 6 0 0 1-6 6h-42v-48h42a6 6 0 0 1 6 6v6h18a6 6 0 0 1 6 6zM30 376h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6zm0-96h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6zm0-96h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6zm0-96h42v48H30a6 6 0 0 1-6-6v-6H6a6 6 0 0 1-6-6v-12a6 6 0 0 1 6-6h18v-6a6 6 0 0 1 6-6z"},"child":[]}]})(props);
}function FaLayerGroup (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M12.41 148.02l232.94 105.67c6.8 3.09 14.49 3.09 21.29 0l232.94-105.67c16.55-7.51 16.55-32.52 0-40.03L266.65 2.31a25.607 25.607 0 0 0-21.29 0L12.41 107.98c-16.55 7.51-16.55 32.53 0 40.04zm487.18 88.28l-58.09-26.33-161.64 73.27c-7.56 3.43-15.59 5.17-23.86 5.17s-16.29-1.74-23.86-5.17L70.51 209.97l-58.1 26.33c-16.55 7.5-16.55 32.5 0 40l232.94 105.59c6.8 3.08 14.49 3.08 21.29 0L499.59 276.3c16.55-7.5 16.55-32.5 0-40zm0 127.8l-57.87-26.23-161.86 73.37c-7.56 3.43-15.59 5.17-23.86 5.17s-16.29-1.74-23.86-5.17L70.29 337.87 12.41 364.1c-16.55 7.5-16.55 32.5 0 40l232.94 105.59c6.8 3.08 14.49 3.08 21.29 0L499.59 404.1c16.55-7.5 16.55-32.5 0-40z"},"child":[]}]})(props);
}function FaGamepad (props) {
  return GenIcon({"attr":{"viewBox":"0 0 640 512"},"child":[{"tag":"path","attr":{"d":"M480.07 96H160a160 160 0 1 0 114.24 272h91.52A160 160 0 1 0 480.07 96zM248 268a12 12 0 0 1-12 12h-52v52a12 12 0 0 1-12 12h-24a12 12 0 0 1-12-12v-52H84a12 12 0 0 1-12-12v-24a12 12 0 0 1 12-12h52v-52a12 12 0 0 1 12-12h24a12 12 0 0 1 12 12v52h52a12 12 0 0 1 12 12zm216 76a40 40 0 1 1 40-40 40 40 0 0 1-40 40zm64-96a40 40 0 1 1 40-40 40 40 0 0 1-40 40z"},"child":[]}]})(props);
}function FaExclamationTriangle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 576 512"},"child":[{"tag":"path","attr":{"d":"M569.517 440.013C587.975 472.007 564.806 512 527.94 512H48.054c-36.937 0-59.999-40.055-41.577-71.987L246.423 23.985c18.467-32.009 64.72-31.951 83.154 0l239.94 416.028zM288 354c-25.405 0-46 20.595-46 46s20.595 46 46 46 46-20.595 46-46-20.595-46-46-46zm-43.673-165.346l7.418 136c.347 6.364 5.609 11.346 11.982 11.346h48.546c6.373 0 11.635-4.982 11.982-11.346l7.418-136c.375-6.874-5.098-12.654-11.982-12.654h-63.383c-6.884 0-12.356 5.78-11.981 12.654z"},"child":[]}]})(props);
}function FaCompactDisc (props) {
  return GenIcon({"attr":{"viewBox":"0 0 496 512"},"child":[{"tag":"path","attr":{"d":"M248 8C111 8 0 119 0 256s111 248 248 248 248-111 248-248S385 8 248 8zM88 256H56c0-105.9 86.1-192 192-192v32c-88.2 0-160 71.8-160 160zm160 96c-53 0-96-43-96-96s43-96 96-96 96 43 96 96-43 96-96 96zm0-128c-17.7 0-32 14.3-32 32s14.3 32 32 32 32-14.3 32-32-14.3-32-32-32z"},"child":[]}]})(props);
}function FaCog (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M487.4 315.7l-42.6-24.6c4.3-23.2 4.3-47 0-70.2l42.6-24.6c4.9-2.8 7.1-8.6 5.5-14-11.1-35.6-30-67.8-54.7-94.6-3.8-4.1-10-5.1-14.8-2.3L380.8 110c-17.9-15.4-38.5-27.3-60.8-35.1V25.8c0-5.6-3.9-10.5-9.4-11.7-36.7-8.2-74.3-7.8-109.2 0-5.5 1.2-9.4 6.1-9.4 11.7V75c-22.2 7.9-42.8 19.8-60.8 35.1L88.7 85.5c-4.9-2.8-11-1.9-14.8 2.3-24.7 26.7-43.6 58.9-54.7 94.6-1.7 5.4.6 11.2 5.5 14L67.3 221c-4.3 23.2-4.3 47 0 70.2l-42.6 24.6c-4.9 2.8-7.1 8.6-5.5 14 11.1 35.6 30 67.8 54.7 94.6 3.8 4.1 10 5.1 14.8 2.3l42.6-24.6c17.9 15.4 38.5 27.3 60.8 35.1v49.2c0 5.6 3.9 10.5 9.4 11.7 36.7 8.2 74.3 7.8 109.2 0 5.5-1.2 9.4-6.1 9.4-11.7v-49.2c22.2-7.9 42.8-19.8 60.8-35.1l42.6 24.6c4.9 2.8 11 1.9 14.8-2.3 24.7-26.7 43.6-58.9 54.7-94.6 1.5-5.5-.7-11.3-5.6-14.1zM256 336c-44.1 0-80-35.9-80-80s35.9-80 80-80 80 35.9 80 80-35.9 80-80 80z"},"child":[]}]})(props);
}function FaChevronDown (props) {
  return GenIcon({"attr":{"viewBox":"0 0 448 512"},"child":[{"tag":"path","attr":{"d":"M207.029 381.476L12.686 187.132c-9.373-9.373-9.373-24.569 0-33.941l22.667-22.667c9.357-9.357 24.522-9.375 33.901-.04L224 284.505l154.745-154.021c9.379-9.335 24.544-9.317 33.901.04l22.667 22.667c9.373 9.373 9.373 24.569 0 33.941L240.971 381.476c-9.373 9.372-24.569 9.372-33.942 0z"},"child":[]}]})(props);
}function FaCheckCircle (props) {
  return GenIcon({"attr":{"viewBox":"0 0 512 512"},"child":[{"tag":"path","attr":{"d":"M504 256c0 136.967-111.033 248-248 248S8 392.967 8 256 119.033 8 256 8s248 111.033 248 248zM227.314 387.314l184-184c6.248-6.248 6.248-16.379 0-22.627l-22.627-22.627c-6.248-6.249-16.379-6.249-22.628 0L216 308.118l-70.059-70.059c-6.248-6.248-16.379-6.248-22.628 0l-22.627 22.627c-6.248 6.248-6.248 16.379 0 22.627l104 104c6.249 6.249 16.379 6.249 22.628.001z"},"child":[]}]})(props);
}

function detach(promise) {
    Promise.resolve(promise).catch(() => undefined);
}

const CACHE_TTL_MS = 3000;
const _cache = new Map();
const _raw = callable("get_cached_game_detail");
function getCachedGameDetail(appId) {
    const now = Date.now();
    const entry = _cache.get(appId);
    if (entry && now - entry.ts < CACHE_TTL_MS)
        return entry.promise;
    const promise = _raw(appId);
    _cache.set(appId, { promise, ts: now });
    promise.then(() => {
        setTimeout(() => {
            _cache.delete(appId);
        }, CACHE_TTL_MS);
    }, () => {
        _cache.delete(appId);
    });
    return promise;
}
function invalidateCachedGameDetail(appId) {
    _cache.delete(appId);
}

function isCallableFailure(value) {
    return "success" in value && value.success === false;
}
function isTargetOccupied(value) {
    return "reason" in value && value.reason === "target_occupied";
}
function isCandidatesFound(value) {
    return "reason" in value && value.reason === "adoption_candidates";
}
function isUnusableNamesake(value) {
    return "reason" in value && value.reason === "unusable_namesake";
}
function isCandidateVanished(value) {
    return "reason" in value && value.reason === "candidate_vanished";
}
function isRenameCollisions(value) {
    return "reason" in value && value.reason === "rename_collisions";
}
const getEmulatorShortcuts = callable("get_emulator_shortcuts");
const bindEmulatorShortcut = callable("bind_emulator_shortcut");
const forgetEmulatorShortcut = callable("forget_emulator_shortcut");
const getEmulatorArtwork = callable("get_emulator_artwork");
const getPlatformEmulators = callable("get_platform_emulators");
const ensurePlatformEmulator = callable("ensure_platform_emulators");
const ensureAllPlatformCores = callable("ensure_all_platform_cores");
const getSettings = callable("get_settings");
const saveServerUrl = callable("save_server_url");
const saveCustomHeaders = callable("save_custom_headers");
const connectWithCredentials = callable("connect_with_credentials");
const connectWithToken = callable("connect_with_token");
const connectWithPairingCode = callable("connect_with_pairing_code");
const signOut = callable("sign_out");
const getWhitelistSettings = callable("get_whitelist_settings");
const updateWhitelistSettings = callable("update_whitelist_settings");
const testConnection = callable("test_connection");
const startSync = callable("start_sync");
const cancelSync = callable("cancel_sync");
const syncHeartbeat = callable("sync_heartbeat");
const syncPreview = callable("sync_preview");
const syncApplyDelta = callable("sync_apply_delta");
const syncCancelPreview = callable("sync_cancel_preview");
const getPendingPreview = callable("get_pending_preview");
const getSyncStatus = callable("get_sync_status");
const getSessionBudgetStatus = callable("get_session_budget_status");
const clearSyncCache = callable("clear_sync_cache");
const getSyncStats = callable("get_sync_stats");
const getSyncRuns = callable("get_sync_runs");
const startDownload = callable("start_download");
const adoptExistingRom = callable("adopt_existing_rom");
const verifyExistingContent = callable("verify_existing_content");
const cancelDownload = callable("cancel_download");
const pauseDownload = callable("pause_download");
const resumeDownload = callable("resume_download");
const getDownloadQueue = callable("get_download_queue");
const clearCompletedDownloads = callable("clear_completed_downloads");
const getInstalledRom = callable("get_installed_rom");
callable("evaluate_launch");
const checkLocalDrift = callable("check_local_drift");
const getRomRelaunchOptions = callable("get_rom_relaunch_options");
const stopRunningGame = callable("stop_running_game");
const probeReachability = callable("probe_reachability");
const refreshSaveStatus$1 = callable("refresh_save_status");
const removeRom = callable("remove_rom");
const getPlatforms = callable("get_platforms");
const savePlatformSync = callable("save_platform_sync");
const setAllPlatformsSync = callable("set_all_platforms_sync");
const getCollections = callable("get_collections");
const saveCollectionSync = callable("save_collection_sync");
const saveCollectionsSync = callable("save_collections_sync");
const setAllCollectionsSync = callable("set_all_collections_sync");
const saveCollectionPlatformGroups = callable("save_collection_platform_groups");
const setCollectionOwnerScope = callable("set_collection_owner_scope");
const setCollectionNamingMode = callable("set_collection_naming_mode");
const getRegistryPlatforms = callable("get_registry_platforms");
const removePlatformShortcuts = callable("remove_platform_shortcuts");
const removeAllShortcuts = callable("remove_all_shortcuts");
const getArtworkBase64 = callable("get_artwork_base64");
const fetchCoverBase64 = callable("fetch_cover_base64");
const refreshCoverArtwork = callable("refresh_cover_artwork");
const cleanupOrphanedGridImages = callable("cleanup_orphaned_grid_images");
const getSgdbArtworkBase64 = callable("get_sgdb_artwork_base64");
const getSgdbResolution = callable("get_sgdb_resolution");
const searchSgdbGames = callable("search_sgdb_games");
const applySgdbGameId = callable("apply_sgdb_game_id");
const reportUnitResults = callable("report_unit_results");
const reportRemovalResults = callable("report_removal_results");
const releaseOrphanedPruneLeases = callable("release_orphaned_prune_leases");
const releasePruneConflictLease = callable("release_prune_conflict_lease");
const renewPruneConflictLease = callable("renew_prune_conflict_lease");
const reconcileShortcuts = callable("reconcile_shortcuts");
const uninstallAllRoms = callable("uninstall_all_roms");
const saveSgdbApiKey = callable("save_sgdb_api_key");
const verifySgdbApiKey = callable("verify_sgdb_api_key");
const saveSteamInputSetting = callable("save_steam_input_setting");
const applySteamInputSetting = callable("apply_steam_input_setting");
const getFirmwareStatus = callable("get_firmware_status");
const getPlatformFirmwareStatus = callable("get_platform_firmware_status");
const downloadAllFirmware = callable("download_all_firmware");
const downloadRequiredFirmware = callable("download_required_firmware");
const downloadPlatformFirmwareFile = callable("download_platform_firmware_file");
const checkPlatformBios = callable("check_platform_bios");
const getBiosStatus = callable("get_bios_status");
const setSystemCore = callable("set_system_core");
const setGameCore = callable("set_game_core");
const clearGameCore = callable("clear_game_core");
const getPlatformCoreInfo = callable("get_platform_core_info");
const getSystemCoreInfo = callable("get_system_core_info");
const getDiscSelection = callable("get_disc_selection");
const selectDisc = callable("select_disc");
const getVersionList = callable("get_version_list");
const switchVersion = callable("switch_version");
const getPrunePreview = callable("get_prune_preview");
const stagePruneInstalledSelection = callable("stage_prune_installed_selection");
const startPrune = callable("start_prune");
const cancelPrune = callable("cancel_prune");
const reportPruneAction = callable("report_prune_action");
const waitForPruneRelease = callable("wait_for_prune_release");
const saveLogLevel = callable("save_log_level");
const savePreferredRegion = callable("save_preferred_region");
const saveSkipPreview = callable("save_skip_preview");
const saveRuntimeMode = callable("save_runtime_mode");
const saveStructure = callable("save_structure");
const getKnownRegions = callable("get_known_regions");
const debugLog = callable("debug_log");
const frontendLog = callable("frontend_log");
const logInfo = (msg) => {
    detach(frontendLog("info", msg));
};
const logWarn = (msg) => {
    detach(frontendLog("warn", msg));
};
const logError = (msg) => {
    detach(frontendLog("error", msg));
};
const fixRetroarchInputDriver = callable("fix_retroarch_input_driver");
const getRomMetadata = callable("get_rom_metadata");
const getMetadataCachePage = callable("get_metadata_cache_page");
const getAppIdRomIdMap = callable("get_app_id_rom_id_map");
const getInstalledRelaunchOptions = callable("get_installed_relaunch_options");
const saveShortcutIcon = callable("save_shortcut_icon");
const ensureDeviceRegistered = callable("ensure_device_registered");
const listDevices = callable("list_devices");
const getSaveStatus = callable("get_save_status");
const preLaunchSync = callable("pre_launch_sync");
const syncRomSaves = callable("sync_rom_saves");
const syncAllSaves = callable("sync_all_saves");
const resolveSyncConflict = callable("resolve_sync_conflict");
const recordSessionStart = callable("record_session_start");
const getSaveSyncSettings = callable("get_save_sync_settings");
const updateSaveSyncSettings = callable("update_save_sync_settings");
const getSaveSlots = callable("get_save_slots");
const getSlotSaves = callable("get_slot_saves");
const switchSlot = callable("switch_slot");
const getSlotDeleteInfo = callable("get_slot_delete_info");
const deleteSlot = callable("delete_slot");
const isSaveTrackingConfigured = callable("is_save_tracking_configured");
const getSaveSetupInfo = callable("get_save_setup_info");
const confirmSlotChoice = callable("confirm_slot_choice");
const checkCoreChange = callable("check_core_change");
const getAllPlaytime = callable("get_all_playtime");
const reconcilePlaytime = callable("reconcile_playtime");
const getRetroDeckStatus = callable("get_retrodeck_status");
const getMigrationStatus = callable("get_migration_status");
const migrateRetroDeckFiles = callable("migrate_retrodeck_files");
const dismissRetrodeckMigration = callable("dismiss_retrodeck_migration");
const getSaveSortMigrationStatus = callable("get_save_sort_migration_status");
const migrateSaveSortFiles = callable("migrate_save_sort_files");
const dismissSaveSortMigration = callable("dismiss_save_sort_migration");
const refreshMigrationState = callable("refresh_migration_state");
const getSettingsResetNotice = callable("get_settings_reset_notice");
const dismissSettingsResetNotice = callable("dismiss_settings_reset_notice");
const getLegacyInstallNotice = callable("get_legacy_install_notice");
const getShortcutRelocation = callable("get_shortcut_relocation");
const dismissLegacyInstallNotice = callable("dismiss_legacy_install_notice");
const getDataLocationNotice = callable("get_data_location_notice");
const getDataLocationCandidates = callable("get_data_location_candidates");
const chooseDataLocation = callable("choose_data_location");
const getPlaytimeScopeNotice = callable("get_playtime_scope_notice");
const finalizeGameSession = callable("finalize_game_session");
const deleteLocalSaves = callable("delete_local_saves");
const deletePlatformSaves = callable("delete_platform_saves");
const countPlatformSaves = callable("count_platform_saves");
const deletePlatformBios = callable("delete_platform_bios");
const deleteBiosFile = callable("delete_bios_file");
const deleteBiosFolder = callable("delete_bios_folder");
const savesListFileVersions = callable("saves_list_file_versions");
const savesRollbackToVersion = callable("saves_rollback_to_version");
const copySaveToSlot = callable("copy_save_to_slot");
const getAchievements = callable("get_achievements");
const getAchievementProgress = callable("get_achievement_progress");
const updatePlugin = callable("update_plugin");

const FOCUS_STOP_SHAPES = ["[tabindex]", "button", "a[href]", "input", "select", "textarea"];
const FOCUS_STOPS = FOCUS_STOP_SHAPES.join(", ");
const ENTRY_STOPS = FOCUS_STOP_SHAPES.map((shape) => `${shape}:not([disabled])`).join(", ");
function firstBodyStop(root) {
    const stops = [...root.querySelectorAll(ENTRY_STOPS)];
    return stops.find((stop) => stop.querySelector(FOCUS_STOPS) === null) ?? null;
}
const ENTRY_STOP_ATTR = "data-romm-entry-stop";
const ENTRY_FOCUS_DELAY_MS = 50;
function pageEntryStop(root) {
    const declared = root.querySelector(`[${ENTRY_STOP_ATTR}]`);
    return (declared === null ? null : firstBodyStop(declared)) ?? firstBodyStop(root);
}
function placeEntryFocus(root, findStop) {
    const stop = findStop(root);
    if (!stop)
        return false;
    stop.focus();
    stop.classList.add("gpfocus");
    return true;
}
function useEntryFocusOnBodySwap(body, bodyKind) {
    const stoodOn = SP_REACT.useRef(null);
    const shown = SP_REACT.useRef(bodyKind);
    SP_REACT.useEffect(() => {
        const root = body.current;
        if (root === null)
            return;
        const took = (event) => {
            stoodOn.current = event.target;
        };
        const left = (event) => {
            const next = event.relatedTarget;
            if (next !== null && !root.contains(next))
                stoodOn.current = null;
        };
        root.addEventListener("focusin", took);
        root.addEventListener("focusout", left);
        return () => {
            root.removeEventListener("focusin", took);
            root.removeEventListener("focusout", left);
        };
    }, [body]);
    SP_REACT.useLayoutEffect(() => {
        const previous = shown.current;
        shown.current = bodyKind;
        if (body.current === null || previous === bodyKind)
            return;
        const stop = stoodOn.current;
        if (stop === null || stop.isConnected)
            return;
        const timer = setTimeout(() => {
            const root = body.current;
            if (root === null)
                return;
            stoodOn.current = null;
            if (!placeEntryFocus(root, firstBodyStop))
                stoodOn.current = stop;
        }, ENTRY_FOCUS_DELAY_MS);
        return () => clearTimeout(timer);
    }, [body, bodyKind]);
}

function formatLastPlayed(timestamp) {
    if (!timestamp || timestamp <= 0)
        return "Never";
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffDays === 0)
        return "Today";
    if (diffDays === 1)
        return "Yesterday";
    if (diffDays < 7)
        return `${diffDays} days ago`;
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const day = date.getDate();
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    if (year === now.getFullYear())
        return `${day}. ${month}.`;
    return `${day}. ${month}. ${year}`;
}
function formatBytes$1(bytes) {
    if (bytes == null)
        return "";
    if (bytes < 1024)
        return `${bytes} B`;
    if (bytes < 1024 * 1024)
        return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024)
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}
function formatPlaytime(minutes) {
    if (!minutes || minutes <= 0)
        return "None";
    if (minutes < 60)
        return `${minutes} Min`;
    const hours = Math.floor(minutes / 60);
    const remainingMin = minutes % 60;
    if (remainingMin === 0)
        return hours === 1 ? "1 Hour" : `${hours} Hours`;
    return `${hours}h ${remainingMin}m`;
}
function formatTimestamp$2(iso) {
    if (!iso)
        return "unknown";
    try {
        const d = new Date(iso);
        return d.toLocaleString(undefined, {
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        });
    }
    catch {
        return iso;
    }
}
function formatTimestampWithYear(iso) {
    if (!iso)
        return "unknown";
    try {
        const d = new Date(iso);
        return d.toLocaleString(undefined, {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    }
    catch {
        return iso;
    }
}
function formatUninstallStatus(removedCount, errorCount) {
    const baseMsg = `Removed ${removedCount} ROMs`;
    return errorCount > 0 ? `${baseMsg} (${errorCount} errors)` : baseMsg;
}
function formatTimeAgo(iso) {
    const ms = Date.parse(iso);
    if (Number.isNaN(ms))
        return null;
    const diffMin = Math.floor((Date.now() - ms) / 60000);
    if (diffMin < 1)
        return "Just now";
    if (diffMin < 60)
        return `${diffMin}m ago`;
    if (diffMin < 1440)
        return `${Math.floor(diffMin / 60)}h ago`;
    return `${Math.floor(diffMin / 1440)}d ago`;
}
const ENTRY_KIND_LABEL = {
    file: "file",
    dir: "folder",
    link: "shortcut to somewhere else",
};

function pluralize(count, singular) {
    return `${count} ${singular}${count === 1 ? "" : "s"}`;
}

const TERMINAL_STAGES = new Set(["done", "cancelled", "error"]);
function isTerminalStage(stage) {
    return !!stage && TERMINAL_STAGES.has(stage);
}
const FETCH_SHARE = 0.15;
const COVERS_SHARE = 0.25;
const APPLY_SHARE = 0.6;
function withinUnitFraction(progress) {
    const current = progress?.current ?? 0;
    const total = progress?.total ?? 0;
    const frac = current > 0 && total > 0 ? Math.min(1, current / total) : 0;
    if (progress?.stage === "applying") {
        return FETCH_SHARE + COVERS_SHARE + APPLY_SHARE * frac;
    }
    if (progress?.stage === "fetching") {
        if (progress.subStage === "covers")
            return FETCH_SHARE + COVERS_SHARE * frac;
        if (progress.subStage === "fetch")
            return FETCH_SHARE * frac;
    }
    return 0;
}
function idleFrame() {
    return { running: false, stage: "", current: 0, total: 0, message: "", runId: "" };
}
let _progress = idleFrame();
let _listeners$b = [];
const _terminatedRunIds = new Set();
function notify$5() {
    _listeners$b.forEach((fn) => {
        try {
            fn();
        }
        catch (e) {
            console.error("[RomM] sync-progress listener threw:", e);
        }
    });
}
function commit(next) {
    const runId = next.runId ?? "";
    const named = runId !== "";
    if (named && next.running && _terminatedRunIds.has(runId))
        return;
    if (named && !next.running && isTerminalStage(next.stage))
        _terminatedRunIds.add(runId);
    _progress = next;
    notify$5();
}
function setSyncProgress(p) {
    commit(p);
}
function updateSyncProgress(p) {
    commit({ ..._progress, ...p });
}
function getSyncProgress() {
    return _progress;
}
function onSyncProgressChange(fn) {
    _listeners$b.push(fn);
    return () => {
        _listeners$b = _listeners$b.filter((l) => l !== fn);
    };
}

const NEW_ITEM_SEC = 0.36;
const UPDATED_ITEM_SEC = 0.13;
const COVER_DOWNLOAD_SEC = 0.15;
const FETCH_ALLOWANCE_SEC = 45;
function estimateApplySeconds(newCount, changedCount, coverRefreshCount = 0) {
    const created = Math.max(0, newCount);
    const updated = Math.max(0, changedCount);
    const refreshed = Math.max(0, coverRefreshCount);
    return (created * NEW_ITEM_SEC +
        updated * UPDATED_ITEM_SEC +
        (created + refreshed) * COVER_DOWNLOAD_SEC +
        FETCH_ALLOWANCE_SEC);
}
function previewApplySeconds(s) {
    return estimateApplySeconds(s.new_count, s.changed_count, s.cover_refresh_count ?? 0);
}
function estimatePlanSeconds(units) {
    let created = 0;
    let updated = 0;
    for (const unit of units) {
        if (unit.predicted_skip)
            continue;
        const items = Math.max(0, unit.collapsed_count ?? unit.rom_count);
        const bound = Math.min(items, Math.max(0, unit.bound_count ?? 0));
        updated += bound;
        created += unit.new_shortcut_count !== undefined ? Math.max(0, unit.new_shortcut_count) : items - bound;
    }
    return estimateApplySeconds(created, updated);
}
function formatApproxDuration(seconds, roundMinutes, suffix) {
    if (seconds < 60)
        return `< 1 min${suffix}`;
    const totalMinutes = roundMinutes(seconds / 60);
    if (totalMinutes < 60)
        return `${totalMinutes} min${suffix}`;
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    return minutes > 0 ? `${hours} h ${minutes} min${suffix}` : `${hours} h${suffix}`;
}
function formatDuration(seconds) {
    return formatApproxDuration(seconds, Math.round, "");
}
function formatTimeRemaining(seconds) {
    return formatApproxDuration(seconds, Math.floor, "");
}

const SAMPLE_MIN_INTERVAL_MS = 1000;
const WINDOW_MS = 30000;
const SEGMENT_BREAK_MS = 10000;
const STALL_GAP_MS = 3000;
const READY_MIN_SAMPLES = 2;
const READY_MIN_SPAN_MS = 5000;
function cumulativeProcessed(unitWeights, step, current) {
    const completedUnits = Math.max(0, step - 1);
    let sum = 0;
    for (let i = 0; i < completedUnits && i < unitWeights.length; i++) {
        sum += Math.max(0, unitWeights[i] ?? 0);
    }
    return sum + Math.max(0, current);
}
function windowedRate(samples) {
    if (samples.length < 2)
        return null;
    const first = samples[0];
    const last = samples[samples.length - 1];
    if (first === undefined || last === undefined)
        return null;
    const spanMs = last.tMs - first.tMs;
    const delta = last.processed - first.processed;
    if (spanMs <= 0 || delta <= 0)
        return null;
    return delta / (spanMs / 1000);
}
function trimStalledPrefix(samples) {
    let start = 0;
    while (start + 1 < samples.length) {
        const head = samples[start];
        const next = samples[start + 1];
        if (head === undefined || next === undefined)
            break;
        const spanMs = next.tMs - head.tMs;
        if (spanMs <= STALL_GAP_MS)
            break;
        if (next.processed - head.processed >= spanMs / SAMPLE_MIN_INTERVAL_MS)
            break;
        start++;
    }
    return samples.slice(start);
}
function remainingSeconds(totalRoms, processed, rate) {
    if (rate <= 0)
        return 0;
    return Math.max(0, (totalRoms - processed) / rate);
}
function formatEtaCountdown(seconds) {
    return formatApproxDuration(seconds, Math.ceil, " left");
}
let _run = null;
function countZeroPrefix(weights) {
    let n = 0;
    while (n < weights.length && Math.max(0, weights[n] ?? 0) <= 0)
        n++;
    return n;
}
function beginEtaRun(runId, unitWeights, totalRoms) {
    _run = {
        runId,
        unitWeights: [...unitWeights],
        totalRoms,
        samples: [],
        lastSampleMs: 0,
        deadlineMs: null,
        zeroPrefix: countZeroPrefix(unitWeights),
        coarseHighWater: 0,
    };
}
function resetEta() {
    _run = null;
}
function observeUnitTotal(unitIndex, unitTotal) {
    if (_run === null)
        return;
    if (unitIndex < 0 || unitIndex >= _run.unitWeights.length)
        return;
    const corrected = Math.max(0, unitTotal);
    const previous = Math.max(0, _run.unitWeights[unitIndex] ?? 0);
    if (corrected === previous)
        return;
    _run.totalRoms = Math.max(0, _run.totalRoms + (corrected - previous));
    _run.unitWeights[unitIndex] = corrected;
    _run.zeroPrefix = Math.max(_run.zeroPrefix, countZeroPrefix(_run.unitWeights));
}
function observeApplyProgress(step, current, tMs) {
    if (_run === null)
        return;
    if (_run.samples.length > 0 && tMs - _run.lastSampleMs > SEGMENT_BREAK_MS) {
        _run.samples = [];
    }
    if (_run.samples.length > 0 && tMs - _run.lastSampleMs < SAMPLE_MIN_INTERVAL_MS)
        return;
    const processed = cumulativeProcessed(_run.unitWeights, step, current);
    _run.samples.push({ tMs, processed });
    _run.lastSampleMs = tMs;
    const cutoff = tMs - WINDOW_MS;
    const recent = _run.samples.filter((s) => s.tMs >= cutoff);
    _run.samples = trimStalledPrefix(recent.length >= 2 ? recent : _run.samples.slice(-2));
    const seconds = liveEtaSeconds();
    if (seconds !== null)
        _run.deadlineMs = tMs + seconds * 1000;
}
function liveEtaSeconds() {
    if (_run === null || _run.samples.length < READY_MIN_SAMPLES)
        return null;
    const first = _run.samples[0];
    const last = _run.samples[_run.samples.length - 1];
    if (first === undefined || last === undefined)
        return null;
    if (last.tMs - first.tMs < READY_MIN_SPAN_MS)
        return null;
    const rate = windowedRate(_run.samples);
    if (rate === null)
        return null;
    return remainingSeconds(_run.totalRoms, last.processed, rate);
}
function displayedEtaSeconds(nowMs) {
    if (_run?.deadlineMs == null)
        return null;
    return Math.max(0, (_run.deadlineMs - nowMs) / 1000);
}
function weightedCoarseFraction(completedUnits, withinUnitFraction, totalUnits) {
    if (_run === null)
        return null;
    const weights = _run.unitWeights;
    if (weights.length !== totalUnits)
        return null;
    let totalWeight = 0;
    for (const w of weights)
        totalWeight += Math.max(0, w);
    if (totalWeight <= 0)
        return null;
    let completedWeight = 0;
    for (let i = 0; i < completedUnits && i < weights.length; i++) {
        completedWeight += Math.max(0, weights[i] ?? 0);
    }
    const runningWeight = completedUnits >= 0 && completedUnits < weights.length ? Math.max(0, weights[completedUnits] ?? 0) : 0;
    const within = Math.max(0, Math.min(1, withinUnitFraction));
    const weighted = Math.min(1, (completedWeight + within * runningWeight) / totalWeight);
    const floor = zeroPrefixFloor(_run.zeroPrefix, completedUnits, within, totalUnits);
    return Math.min(1, floor + (1 - floor) * weighted);
}
function latchedCoarseFraction(completedUnits, withinUnitFraction, totalUnits) {
    const fraction = weightedCoarseFraction(completedUnits, withinUnitFraction, totalUnits);
    if (fraction === null || _run === null)
        return fraction;
    const latched = Math.max(fraction, _run.coarseHighWater);
    _run.coarseHighWater = latched;
    return latched;
}
function zeroPrefixFloor(zeroPrefix, completedUnits, within, totalUnits) {
    if (totalUnits <= 0)
        return 0;
    const reached = Math.min(Math.max(0, completedUnits), zeroPrefix);
    const stillInside = completedUnits < zeroPrefix;
    return (reached + (stillInside ? within : 0)) / totalUnits;
}

const STAGE_LABELS$1 = {
    discovering: "Discovering platforms",
    fetching: "Fetching library",
    applying: "Applying shortcuts",
    finalizing: "Finalizing",
    done: "Done",
    cancelled: "Cancelled",
    error: "Error",
};
function stageLabel$1(stage) {
    return stage ? STAGE_LABELS$1[stage] : "Syncing";
}
function formatProgressText(progress) {
    if (!progress)
        return "Syncing...";
    return progress.message || "Syncing...";
}
function frameRunId(progress) {
    return progress.runId ?? "";
}
function inFlightRunId(progress) {
    return progress.running ? frameRunId(progress) : null;
}
function endsWatchedRun(watched, runId) {
    return watched !== null && (watched === "" || runId === "" || watched === runId);
}
function useSyncRunView(options = {}) {
    const [progress, setProgress] = SP_REACT.useState(() => getSyncProgress());
    const [carriedFineDetail, setCarriedFineDetail] = SP_REACT.useState(null);
    const [liveEtaDisplay, setLiveEtaDisplay] = SP_REACT.useState(null);
    const watchedRunId = SP_REACT.useRef(inFlightRunId(getSyncProgress()));
    const watchedRunEnded = SP_REACT.useRef(false);
    const callbacks = SP_REACT.useRef(options);
    SP_REACT.useEffect(() => {
        callbacks.current = options;
    });
    SP_REACT.useEffect(() => {
        const endWatchedRun = (frame) => {
            resetEta();
            setLiveEtaDisplay(null);
            callbacks.current.onRunEnd?.(frame);
        };
        const correctTerminalWording = (message, stage) => {
            callbacks.current.onTerminalWording?.(message, stage);
        };
        const advanceLiveEta = (frame) => {
            if (frame.stage === "applying" &&
                frame.step !== undefined &&
                frame.current !== undefined &&
                !frame.coverRefresh) {
                observeApplyProgress(frame.step, frame.current, Date.now());
            }
            setLiveEtaDisplay(displayedEtaSeconds(Date.now()));
        };
        return onSyncProgressChange(() => {
            const frame = getSyncProgress();
            setProgress(frame);
            const inFlight = inFlightRunId(frame);
            if (inFlight !== null) {
                watchedRunId.current = inFlight;
                watchedRunEnded.current = false;
            }
            const terminal = isTerminalStage(frame.stage);
            const runEndedNow = terminal && !watchedRunEnded.current && endsWatchedRun(watchedRunId.current, frameRunId(frame));
            const laterTerminalFrame = terminal && watchedRunEnded.current;
            if (runEndedNow)
                watchedRunEnded.current = true;
            if (!frame.running) {
                setCarriedFineDetail(null);
            }
            else if (frame.message && (frame.total || frame.totalSteps)) {
                setCarriedFineDetail(frame.message);
            }
            try {
                if (runEndedNow) {
                    endWatchedRun(frame);
                }
                else if (laterTerminalFrame && frame.message) {
                    correctTerminalWording(frame.message, frame.stage);
                }
                else if (!terminal) {
                    advanceLiveEta(frame);
                }
            }
            catch (e) {
                logError(`sync-progress subscriber failed: ${e}`);
            }
        });
    }, []);
    const step = progress?.step ?? 0;
    const activeUnit = progress?.stage === "fetching" || progress?.stage === "applying";
    const completedSteps = activeUnit ? Math.max(0, step - 1) : step;
    const withinUnit = withinUnitFraction(progress);
    const weightedFraction = progress?.totalSteps
        ? latchedCoarseFraction(completedSteps, withinUnit, progress.totalSteps)
        : null;
    const coarseFraction = progress?.totalSteps
        ? Math.max(0, Math.min(100, (weightedFraction ?? (completedSteps + withinUnit) / progress.totalSteps) * 100))
        : undefined;
    const currentHasFineDetail = !!(progress?.total && progress.message);
    const hasFineDetail = currentHasFineDetail || carriedFineDetail !== null;
    const fineDetailText = currentHasFineDetail ? formatProgressText(progress) : (carriedFineDetail ?? "");
    const staticEtaSeconds = progress?.etaSeconds;
    let etaText = null;
    if (liveEtaDisplay !== null) {
        etaText = formatEtaCountdown(liveEtaDisplay);
    }
    else if (staticEtaSeconds !== undefined) {
        etaText = `up to ${formatDuration(staticEtaSeconds)}`;
    }
    return {
        running: progress?.running ?? false,
        stage: progress?.stage,
        runKind: progress?.runKind ? progress.runKind : null,
        stageLabel: stageLabel$1(progress?.stage),
        step,
        totalSteps: progress?.totalSteps ?? 0,
        withinUnitFraction: withinUnit,
        coarseFraction,
        hasFineDetail,
        fineDetailText,
        etaText,
        runId: progress?.runId ?? "",
    };
}

let _downloads = [];
const _listeners$a = new Set();
function notify$4() {
    _listeners$a.forEach((fn) => fn());
}
function sameEntries(a, b) {
    return a.length === b.length && a.every((item, i) => item === b[i]);
}
function setDownloads(items) {
    if (sameEntries(_downloads, items))
        return;
    _downloads = items.slice();
    notify$4();
}
function updateDownload(item) {
    const idx = _downloads.findIndex((d) => d.rom_id === item.rom_id);
    if (idx >= 0) {
        if (_downloads[idx] === item)
            return;
        const next = _downloads.slice();
        next[idx] = item;
        _downloads = next;
    }
    else {
        _downloads = [..._downloads, item];
    }
    notify$4();
}
function removeDownload(romId) {
    const next = _downloads.filter((d) => d.rom_id !== romId);
    if (next.length === _downloads.length)
        return;
    _downloads = next;
    notify$4();
}
function getDownloadState() {
    return _downloads;
}
function removeTerminalDownloads() {
    const next = _downloads.filter((d) => d.status !== "completed" && d.status !== "failed" && d.status !== "cancelled");
    if (next.length === _downloads.length)
        return;
    _downloads = next;
    notify$4();
}
function onDownloadsChange(fn) {
    _listeners$a.add(fn);
    return () => {
        _listeners$a.delete(fn);
    };
}
function useDownloads() {
    return SP_REACT.useSyncExternalStore(onDownloadsChange, getDownloadState);
}

let _preview = null;
let _issued = 0;
let _applied = 0;
const _listeners$9 = new Set();
function notify$3() {
    _listeners$9.forEach((fn) => fn());
}
function apply(seq, value) {
    if (seq <= _applied)
        return;
    _applied = seq;
    if (_preview === value)
        return;
    _preview = value;
    notify$3();
}
function getPendingPreviewSnapshot() {
    return _preview;
}
function onPendingPreviewChange(fn) {
    _listeners$9.add(fn);
    return () => {
        _listeners$9.delete(fn);
    };
}
function usePendingPreview() {
    return SP_REACT.useSyncExternalStore(onPendingPreviewChange, getPendingPreviewSnapshot);
}
function adoptPreview(preview) {
    apply(++_issued, preview);
}
function clearPendingPreview() {
    apply(++_issued, null);
}
function refreshPendingPreview() {
    const seq = ++_issued;
    return getPendingPreview().then((answer) => {
        if (!answer.success || !answer.preview)
            return;
        apply(seq, answer.preview);
    }, (e) => logError(`Failed to query pending preview: ${e}`));
}

const PREVIEW_COUNTDOWN_TICK_MS = 1000;
function previewHasChanges(preview) {
    const s = preview.summary;
    return (s.new_count + s.changed_count + s.remove_count > 0 ||
        !!(s.collection_diff?.added.length || s.collection_diff?.removed.length) ||
        !!s.platform_collection_diff?.has_changes ||
        (s.cover_refresh_count ?? 0) > 0 ||
        (s.restamp_platform_count ?? 0) > 0);
}
function previewSecondsLeft(preview, nowMs) {
    if (preview.expires_at === undefined)
        return null;
    return Math.max(0, preview.expires_at - nowMs / 1000);
}

const _listeners$8 = new Set();
function notify$2() {
    _listeners$8.forEach((fn) => fn());
}
const _stats = {
    value: null,
    read: getSyncStats,
    issued: 0,
    applied: 0,
    open: null,
    failed: false,
    failureLabel: "Failed to load sync stats",
};
const _budget = {
    value: null,
    read: getSessionBudgetStatus,
    issued: 0,
    applied: 0,
    open: null,
    failed: false,
    failureLabel: "Failed to load session budget status",
};
function applyAnswer(lane, seq, value) {
    if (seq <= lane.applied)
        return;
    lane.applied = seq;
    lane.value = value;
    lane.failed = false;
    notify$2();
}
function recordFailure(lane, seq) {
    if (seq <= lane.applied)
        return;
    lane.failed = true;
    notify$2();
}
function issueRead(lane) {
    const seq = ++lane.issued;
    const request = lane
        .read()
        .then((value) => applyAnswer(lane, seq, value), (e) => {
        logError(`${lane.failureLabel}: ${e}`);
        recordFailure(lane, seq);
    })
        .finally(() => {
        if (lane.open === request)
            lane.open = null;
    });
    lane.open = request;
    return request;
}
function joinOrIssue(lane) {
    return lane.open ?? issueRead(lane);
}
function getSyncStatsSnapshot() {
    return _stats.value;
}
function getSessionBudgetSnapshot() {
    return _budget.value;
}
function getSyncStatsFailedSnapshot() {
    return _stats.failed;
}
function onSyncStatsStoreChange(fn) {
    _listeners$8.add(fn);
    return () => {
        _listeners$8.delete(fn);
    };
}
function useSyncStats() {
    return SP_REACT.useSyncExternalStore(onSyncStatsStoreChange, getSyncStatsSnapshot);
}
function useSyncStatsFailed() {
    return SP_REACT.useSyncExternalStore(onSyncStatsStoreChange, getSyncStatsFailedSnapshot);
}
function useSessionBudget() {
    return SP_REACT.useSyncExternalStore(onSyncStatsStoreChange, getSessionBudgetSnapshot);
}
function refreshSyncStats() {
    return joinOrIssue(_stats);
}
function refreshSyncStatsAfterChange() {
    return issueRead(_stats);
}
function refreshSessionBudget() {
    return joinOrIssue(_budget);
}
function refreshSessionBudgetAfterChange() {
    return issueRead(_budget);
}

let _migration = { pending: false };
let _listeners$7 = [];
function setMigrationStatus(status) {
    _migration = status;
    _listeners$7.forEach((fn) => fn());
}
function getMigrationState() {
    return _migration;
}
function clearMigration() {
    _migration = { pending: false };
    _listeners$7.forEach((fn) => fn());
}
function onMigrationChange(fn) {
    _listeners$7.push(fn);
    return () => {
        _listeners$7 = _listeners$7.filter((l) => l !== fn);
    };
}
function useMigrationStatus() {
    return SP_REACT.useSyncExternalStore(onMigrationChange, getMigrationState);
}

let _state$6 = { pending: false, backedUpTo: null };
let _listeners$6 = [];
function setSettingsResetState(state) {
    _state$6 = state;
    _listeners$6.forEach((fn) => fn());
}
function getSettingsResetState() {
    return _state$6;
}
function onSettingsResetChange(fn) {
    _listeners$6.push(fn);
    return () => {
        _listeners$6 = _listeners$6.filter((l) => l !== fn);
    };
}
function useSettingsResetState() {
    return SP_REACT.useSyncExternalStore(onSettingsResetChange, getSettingsResetState);
}
async function fetchSettingsResetState() {
    const notice = await getSettingsResetNotice();
    const next = { pending: notice.pending, backedUpTo: notice.backed_up_to };
    setSettingsResetState(next);
    return next;
}

let _state$5 = { pending: false };
let _listeners$5 = [];
function setPlaytimeScopeState(state) {
    _state$5 = state;
    _listeners$5.forEach((fn) => fn());
}
function getPlaytimeScopeState() {
    return _state$5;
}
function onPlaytimeScopeChange(fn) {
    _listeners$5.push(fn);
    return () => {
        _listeners$5 = _listeners$5.filter((l) => l !== fn);
    };
}
function usePlaytimeScopeState() {
    return SP_REACT.useSyncExternalStore(onPlaytimeScopeChange, getPlaytimeScopeState);
}
async function fetchPlaytimeScopeState() {
    const notice = await getPlaytimeScopeNotice();
    const next = { pending: notice.pending };
    setPlaytimeScopeState(next);
    return next;
}

let _status = { pending: false };
let _listeners$4 = [];
function setSaveSortMigrationStatus(status) {
    _status = status;
    _listeners$4.forEach((fn) => fn());
}
function getSaveSortMigrationState() {
    return _status;
}
function clearSaveSortMigration() {
    _status = { pending: false };
    _listeners$4.forEach((fn) => fn());
}
function onSaveSortMigrationChange(fn) {
    _listeners$4.push(fn);
    return () => {
        _listeners$4 = _listeners$4.filter((l) => l !== fn);
    };
}
function useSaveSortMigrationState() {
    return SP_REACT.useSyncExternalStore(onSaveSortMigrationChange, getSaveSortMigrationState);
}

const delay = (ms) => new Promise((r) => setTimeout(r, ms));
async function pacedForEach(items, fn, options = {}) {
    const { chunkSize = 1, delayMs = 50, heartbeat, heartbeatIntervalMs = 10000, isCancelled, onProgress } = options;
    let lastHeartbeat = Date.now();
    for (const [i, item] of items.entries()) {
        try {
            await fn(item, i);
        }
        catch (e) {
            logError(`pacedForEach: item ${i} failed: ${e}`);
        }
        const done = i + 1;
        onProgress?.(done);
        if (done % chunkSize === 0 && done < items.length) {
            await delay(delayMs);
        }
        if (heartbeat && Date.now() - lastHeartbeat > heartbeatIntervalMs) {
            heartbeat();
            lastHeartbeat = Date.now();
        }
        if (isCancelled?.())
            return false;
    }
    return true;
}

const ROM_LAUNCHER_SUFFIX = "/bin/rom-launcher";
function isRomMShortcutDetails(details) {
    return (typeof details?.strShortcutExe === "string" &&
        details.strShortcutExe.replace(/^"|"$/g, "").endsWith(ROM_LAUNCHER_SUFFIX));
}
const HEARTBEAT_INTERVAL_MS = 10000;
function getAppDetails(appId, timeoutMs = 2000) {
    return new Promise((resolve) => {
        let resolved = false;
        let reg;
        const finish = (value) => {
            if (resolved)
                return;
            resolved = true;
            reg?.unregister();
            resolve(value);
        };
        reg = SteamClient.Apps.RegisterForAppDetails(appId, (details) => {
            if (details)
                finish(details);
        });
        setTimeout(() => finish(null), timeoutMs);
    });
}
function setLaunchOptionsConfirmed(appId, value, timeoutMs = 2000) {
    return new Promise((resolve) => {
        let resolved = false;
        let reg;
        const finish = (matched) => {
            if (resolved)
                return;
            resolved = true;
            reg?.unregister();
            resolve(matched);
        };
        SteamClient.Apps.SetAppLaunchOptions(appId, value);
        reg = SteamClient.Apps.RegisterForAppDetails(appId, (details) => {
            if (!details)
                return;
            const current = details.strLaunchOptions ?? details.LaunchOptions ?? "";
            if (current === value)
                finish(true);
        });
        setTimeout(() => finish(false), timeoutMs);
    });
}
async function getLiveRomMShortcutAppIds() {
    if (typeof collectionStore === "undefined")
        return null;
    const deckApps = collectionStore.deckDesktopApps?.apps;
    if (!deckApps)
        return null;
    const appIds = Array.from(deckApps.keys());
    const ourAppIds = [];
    const CONCURRENCY = 10;
    let lastHeartbeat = Date.now();
    for (let i = 0; i < appIds.length; i += CONCURRENCY) {
        const batch = appIds.slice(i, i + CONCURRENCY);
        const entries = await Promise.all(batch.map((appId) => getAppDetails(appId).then((details) => ({ appId, exe: details?.strShortcutExe ?? "" }))));
        for (const { appId, exe } of entries) {
            if (exe.endsWith(ROM_LAUNCHER_SUFFIX))
                ourAppIds.push(appId);
        }
        if (Date.now() - lastHeartbeat > HEARTBEAT_INTERVAL_MS) {
            syncHeartbeat().catch(() => { });
            lastHeartbeat = Date.now();
        }
    }
    return ourAppIds;
}
function getAllNonSteamShortcutAppIds() {
    if (typeof collectionStore === "undefined")
        return null;
    const deckApps = collectionStore.deckDesktopApps?.apps;
    if (!deckApps)
        return null;
    return Array.from(deckApps.keys());
}
async function getExistingRomMShortcuts(preScanned) {
    const result = new Map();
    const ourAppIds = preScanned !== undefined ? preScanned : await getLiveRomMShortcutAppIds();
    if (!ourAppIds || ourAppIds.length === 0)
        return result;
    let appIdToRomId;
    try {
        appIdToRomId = await getAppIdRomIdMap();
    }
    catch (e) {
        logError(`getExistingRomMShortcuts: failed to load app-id↔rom-id map: ${e}`);
        return result;
    }
    for (const appId of ourAppIds) {
        const romId = appIdToRomId[String(appId)];
        if (typeof romId === "number")
            result.set(romId, appId);
    }
    return result;
}
async function waitForAppOverview(appId, timeoutMs) {
    const POLL_INTERVAL_MS = 100;
    const deadline = Date.now() + timeoutMs;
    for (;;) {
        if (appStore.GetAppOverviewByAppID(appId))
            return true;
        if (Date.now() >= deadline)
            return false;
        await delay(POLL_INTERVAL_MS);
    }
}
async function addShortcut(data) {
    try {
        const appId = await SteamClient.Apps.AddShortcut(data.name, data.exe, "", "");
        if (!appId)
            return null;
        if (!(await waitForAppOverview(appId, 1000))) {
            logInfo(`addShortcut: overview for ${appId} not ready within 1000ms; proceeding anyway`);
        }
        SteamClient.Apps.SetShortcutName(appId, data.name);
        SteamClient.Apps.SetShortcutExe(appId, data.exe);
        SteamClient.Apps.SetShortcutStartDir(appId, data.start_dir);
        if (data.launch_options !== "") {
            await setLaunchOptionsConfirmed(appId, data.launch_options);
        }
        return appId;
    }
    catch (e) {
        logError(`Failed to add shortcut for ${data.name}: ${e}`);
        return null;
    }
}
function removeShortcut(appId) {
    try {
        SteamClient.Apps.RemoveShortcut(appId);
    }
    catch (e) {
        logError(`Failed to remove shortcut ${appId}: ${e}`);
    }
}
function readDesktopAppStore() {
    if (typeof collectionStore === "undefined")
        return null;
    return collectionStore.deckDesktopApps?.apps ?? null;
}
async function removeShortcutConfirmedOutcome(appId, timeoutMs = 3000, ownershipAlreadyChecked = false) {
    const store = readDesktopAppStore();
    if (!store?.has(appId))
        return { status: "not_attempted" };
    if (!ownershipAlreadyChecked && !isRomMShortcutDetails(await getAppDetails(appId))) {
        return { status: "not_attempted" };
    }
    try {
        SteamClient.Apps.RemoveShortcut(appId);
    }
    catch (e) {
        logError(`Failed to remove shortcut ${appId}: ${e}`);
        return { status: "not_attempted" };
    }
    const deadline = Date.now() + timeoutMs;
    for (;;) {
        const apps = readDesktopAppStore();
        if (!apps)
            return { status: "attempted_unconfirmed" };
        if (!apps.has(appId))
            return { status: "confirmed" };
        if (Date.now() >= deadline)
            return { status: "attempted_unconfirmed" };
        await delay(100);
    }
}

const created = new Set();
const removed = new Set();
function resetSyncDelta() {
    created.clear();
    removed.clear();
}
function recordSyncCreated(appId) {
    created.add(appId);
}
function recordSyncRemoved(appId) {
    removed.add(appId);
}
function getSyncDelta() {
    return { added: created.size, removed: removed.size };
}

let _units = [];
let _runId = null;
const _listeners$3 = new Set();
function notify$1() {
    _listeners$3.forEach((fn) => fn());
}
function getRunUnitsSnapshot() {
    return _units;
}
function onRunUnitsChange(fn) {
    _listeners$3.add(fn);
    return () => {
        _listeners$3.delete(fn);
    };
}
function useRunUnits() {
    return SP_REACT.useSyncExternalStore(onRunUnitsChange, getRunUnitsSnapshot);
}
function seedRunUnits(units, runId) {
    _runId = runId;
    _units = units.map((unit) => ({
        id: unit.id,
        type: unit.type,
        name: unit.name,
        romCount: unit.rom_count,
        predictedSkip: unit.predicted_skip ?? false,
        boundCount: unit.bound_count ?? null,
        newShortcutCount: unit.new_shortcut_count ?? null,
        state: "waiting",
        created: 0,
        updated: 0,
    }));
    notify$1();
}
function clearRunUnits() {
    _units = [];
    _runId = null;
    notify$1();
}
function recordUnitCreated(unitIndex) {
    recordUnitOutcome(unitIndex, 1, 0);
}
function recordUnitUpdated(unitIndex) {
    recordUnitOutcome(unitIndex, 0, 1);
}
function recordUnitOutcome(unitIndex, created, updated) {
    const unit = _units[unitIndex];
    if (unit === undefined)
        return;
    _units = _units.map((row, i) => i === unitIndex ? { ...row, created: row.created + created, updated: row.updated + updated } : row);
    notify$1();
}
function attachRunUnitsMirror() {
    return onSyncProgressChange(() => observeRunFrame(getSyncProgress()));
}
function isActiveUnitStage(stage) {
    return stage === "fetching" || stage === "applying";
}
function withState(unit, state) {
    return unit.state === state ? unit : { ...unit, state };
}
function observeRunFrame(progress) {
    if (!progress.running || _runId === null || _units.length === 0)
        return;
    if ((progress.runId ?? "") !== _runId)
        return;
    const step = progress.step ?? 0;
    if (step <= 0 || step > _units.length)
        return;
    if (progress.totalSteps !== undefined && progress.totalSteps !== _units.length)
        return;
    const active = isActiveUnitStage(progress.stage);
    const runningIndex = active ? step - 1 : -1;
    const completed = active ? step - 1 : step;
    const next = _units.map((unit, i) => {
        if (i < completed)
            return withState(unit, "done");
        if (i === runningIndex)
            return withState(unit, "running");
        return unit;
    });
    if (next.every((unit, i) => unit === _units[i]))
        return;
    _units = next;
    notify$1();
}

const appActionButtonClasses = DFL.appActionButtonClasses;
const basicAppDetailsSectionStylerClasses = DFL.basicAppDetailsSectionStylerClasses;
const appDetailsClasses = DFL.appDetailsClasses;
const playSectionClasses = DFL.playSectionClasses;
const Tabs = DFL.Tabs;
const ScrollPanel = DFL.ScrollPanel;
const findSP = () => DFL.findSP();
const GLYPH_BUTTON_B = 1;
const isMemoComponent = (value) => typeof value === "object" && value !== null && value.$$typeof === Symbol.for("react.memo");
const ControllerGlyph = DFL.findModule((m) => {
    try {
        if (typeof m !== "object" || m === null)
            return false;
        const exports = m;
        const names = Object.keys(exports);
        return names.length === 2 && isMemoComponent(exports.W) && isMemoComponent(exports.X);
    }
    catch {
        return false;
    }
})?.W;

const ROMM_PLAY_HIDE_ID = "romm-hide-native-play";
const ROMM_FOCUS_STYLES_ID = "romm-focus-styles";
const ROMM_INFO_ITEMS_ID = "romm-info-items-styles";
const ROMM_GAME_INFO_PANEL_ID = "romm-game-info-panel-styles";
const ROMM_GEAR_BUTTONS_ID = "romm-gear-btn-styles";
const ROMM_TABS_ID = "romm-tabs-styles";
const ROMM_ACHIEVEMENTS_ID = "romm-achievements-styles";
function hideNativePlaySection(playSectionClass) {
    const sp = findSP();
    if (!sp?.window.document)
        return;
    if (!sp.window.document.getElementById(ROMM_PLAY_HIDE_ID)) {
        const style = sp.window.document.createElement("style");
        style.id = ROMM_PLAY_HIDE_ID;
        style.textContent = `.${playSectionClass}:not([data-romm]) {
  display: none !important;
  visibility: hidden !important;
  pointer-events: none !important;
}`;
        sp.window.document.head.appendChild(style);
    }
    if (!sp.window.document.getElementById(ROMM_FOCUS_STYLES_ID)) {
        const focusStyle = sp.window.document.createElement("style");
        focusStyle.id = ROMM_FOCUS_STYLES_ID;
        focusStyle.textContent = `
/* Blue hover/focus highlight is scoped to the IDLE Download button
   (romm-btn-download-idle): its base is already blue, so brightening to blue is
   correct. The active download button (downloading/paused/extracting) shares
   romm-btn-download for position/overflow but has a dark base under a green
   progress fill — this !important blue must NOT reach it, or a focused/hovered
   active button (e.g. the rehydrated paused one that the initial-focus grab
   gpfocus-marks) repaints its dark remainder bright blue. */
.romm-btn-download-idle:hover, .romm-btn-download-idle.gpfocus {
  background: linear-gradient(to right, #47b3ff, #1a9fff) !important;
  filter: brightness(1.3);
}
.romm-btn-play:hover, .romm-btn-play.gpfocus {
  background: linear-gradient(to right, #80e62a, #01b866) !important;
  filter: brightness(1.2);
}
.romm-btn-play.romm-offline:hover, .romm-btn-play.romm-offline.gpfocus {
  background: linear-gradient(to right, #7a8b7a, #6b7b6b) !important;
  filter: brightness(1.1);
}
.romm-btn-conflict:hover, .romm-btn-conflict.gpfocus {
  background: linear-gradient(to right, #c49a28, #a6851b) !important;
  filter: brightness(1.2);
}
.romm-btn-dropdown:hover, .romm-btn-dropdown.gpfocus {
  filter: brightness(1.3);
}
.romm-btn-cancel:hover, .romm-btn-cancel.gpfocus, .romm-btn-cancel:focus {
  background: rgba(255, 255, 255, 0.25) !important;
}
[data-romm] .gpfocus {
  outline: 2px solid #1a9fff;
  outline-offset: 2px;
}
.romm-wizard-btn:hover,
.romm-wizard-btn:focus,
.romm-wizard-btn.gpfocus {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.7) !important;
  outline: 2px solid #1a9fff !important;
  outline-offset: 2px;
}
.romm-wizard-btn-primary:hover,
.romm-wizard-btn-primary:focus,
.romm-wizard-btn-primary.gpfocus {
  background: rgba(26, 159, 255, 0.3) !important;
  border-color: rgba(26, 159, 255, 0.9) !important;
  outline: 2px solid #1a9fff !important;
  outline-offset: 2px;
}
@keyframes romm-spin {
  to { transform: rotate(360deg); }
}
.romm-throbber {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: romm-spin 0.8s linear infinite;
  flex-shrink: 0;
}
@keyframes romm-dl-pulse {
  0%, 100% { box-shadow: 0 0 4px var(--romm-pulse-color, rgba(26,159,255,0.3)); }
  50% { box-shadow: 0 0 20px var(--romm-pulse-color, rgba(26,159,255,0.7)); }
}
@keyframes romm-dl-complete {
  0% { box-shadow: 0 0 0px rgba(112,214,29,0); filter: brightness(1); transform: scale(1); }
  12% { box-shadow: 0 0 50px rgba(112,214,29,1), inset 0 0 25px rgba(255,255,255,0.4); filter: brightness(2.2); transform: scale(1.06); }
  30% { box-shadow: 0 0 30px rgba(112,214,29,0.7), inset 0 0 12px rgba(255,255,255,0.2); filter: brightness(1.5); transform: scale(1.02); }
  60% { box-shadow: 0 0 15px rgba(112,214,29,0.4), inset 0 0 5px rgba(255,255,255,0.08); filter: brightness(1.2); transform: scale(1); }
  100% { box-shadow: 0 0 0px rgba(112,214,29,0); filter: brightness(1.2); transform: scale(1); }
}
.romm-btn-download {
  position: relative;
  overflow: hidden;
}
.romm-dl-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 0%;
  transition: width 0.4s ease-out;
  pointer-events: none;
  z-index: 0;
}
.romm-dl-active-group {
  border-radius: 2px;
  animation: romm-dl-pulse 2s ease-in-out infinite;
}
.romm-dl-label {
  position: relative;
  z-index: 2;
}
.romm-dl-complete-flash {
  animation: romm-dl-complete 1s ease-out forwards;
}
@keyframes romm-dl-uninstall {
  0% { box-shadow: 0 0 0px rgba(26,159,255,0); filter: brightness(0.4); transform: scale(0.95); }
  40% { box-shadow: 0 0 35px rgba(26,159,255,0.8); filter: brightness(1.5); transform: scale(1.03); }
  100% { box-shadow: 0 0 0px rgba(26,159,255,0); filter: brightness(1.3); transform: scale(1); }
}
.romm-dl-uninstall-flash {
  animation: romm-dl-uninstall 0.5s ease-out forwards;
}`;
        sp.window.document.head.appendChild(focusStyle);
    }
    if (!sp.window.document.getElementById(ROMM_INFO_ITEMS_ID)) {
        const infoStyle = sp.window.document.createElement("style");
        infoStyle.id = ROMM_INFO_ITEMS_ID;
        infoStyle.textContent = `
.romm-info-items {
  margin-left: 16px;
}
.romm-info-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
}
.romm-info-header {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #8f98a0;
  line-height: 1.2;
  white-space: nowrap;
}
.romm-info-value {
  font-size: 13px;
  font-weight: 500;
  color: #dcdedf;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.romm-info-muted .romm-info-value {
  color: #5e6770;
  font-style: italic;
}
.romm-status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
@keyframes romm-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
.romm-status-dot-pulse {
  animation: romm-pulse 1.5s ease-in-out infinite;
}`;
        sp.window.document.head.appendChild(infoStyle);
    }
    if (!sp.window.document.getElementById(ROMM_GAME_INFO_PANEL_ID)) {
        const panelStyle = sp.window.document.createElement("style");
        panelStyle.id = ROMM_GAME_INFO_PANEL_ID;
        panelStyle.textContent = `
.romm-panel-container {
  display: flex;
  flex-direction: column;
  padding: 16px 2.8vw;
  gap: 16px;
  background: rgba(14, 20, 27, 0.33);
}
.romm-panel-section {
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
}
.romm-panel-section:last-child {
  border-bottom: none;
  padding-bottom: 0;
}
.romm-panel-section-title {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #8f98a0;
  margin-bottom: 8px;
  line-height: 1.2;
}
.romm-panel-rom-name {
  color: #ffffff;
  font-size: 16px;
  font-weight: 700;
  line-height: 1.25;
  margin-bottom: 8px;
}
.romm-panel-summary {
  color: #acb2b8;
  font-size: 13px;
  line-height: 1.5;
  margin-bottom: 8px;
}
.romm-panel-info-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
  padding: 2px 0;
}
.romm-panel-label {
  color: #8f98a0;
  font-size: 12px;
  flex-shrink: 0;
  min-width: 120px;
}
.romm-panel-value {
  color: #dcdedf;
  font-size: 13px;
}
.romm-panel-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.romm-panel-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  background: rgba(255,255,255,0.06);
  color: #8f98a0;
  border: 1px solid rgba(255,255,255,0.1);
}
.romm-panel-status-row {
  display: flex;
  gap: 12px;
  align-items: center;
}
.romm-panel-status-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 3px;
  font-weight: 600;
}
.romm-panel-status-installed {
  background: rgba(91,163,43,0.2);
  color: #5ba32b;
}
.romm-panel-status-not-installed {
  background: rgba(143,152,160,0.15);
  color: #8f98a0;
}
.romm-panel-platform-badge {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 3px;
  font-weight: 600;
  background: rgba(26,159,255,0.15);
  color: #1a9fff;
}
.romm-panel-actions-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.romm-panel-action-btn {
  font-size: 12px;
  padding: 6px 14px;
  border-radius: 3px;
  background: rgba(255,255,255,0.06);
  color: #dcdedf;
  border: 1px solid rgba(255,255,255,0.1);
  cursor: pointer;
}
.romm-panel-action-btn:hover, .romm-panel-action-btn.gpfocus {
  background: rgba(255,255,255,0.12);
  filter: brightness(1.1);
}
.romm-panel-action-destructive {
  color: #d94126;
  border-color: rgba(217,65,38,0.3);
}
.romm-panel-action-destructive:hover, .romm-panel-action-destructive.gpfocus {
  background: rgba(217,65,38,0.15);
}
.romm-panel-muted {
  color: #5e6770;
  font-size: 13px;
  font-style: italic;
}
.romm-panel-loading {
  color: #8f98a0;
  font-size: 13px;
  padding: 8px 0;
}
.romm-panel-status-action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.romm-panel-status-inline {
  display: flex;
  align-items: center;
  gap: 8px;
}
.romm-panel-file-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 8px 0;
}
.romm-panel-file-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}
.romm-panel-file-name {
  font-size: 12px;
  color: #dcdedf;
  font-weight: 500;
}
.romm-panel-file-path {
  font-size: 11px;
  color: #5e6770;
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
.romm-panel-file-detail {
  font-size: 11px;
  color: #8f98a0;
  white-space: nowrap;
}
.romm-panel-file-conflict {
  font-size: 11px;
  color: #d94126;
  font-weight: 600;
}
/* Slot panel (collapsible) */
.romm-slot-panel {
  margin-bottom: 8px;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  overflow: hidden;
}
.romm-slot-panel-active {
  border-color: rgba(91,163,43,0.3);
}
/* Legacy (RomM web-player) bucket — read-only, visually demoted */
.romm-slot-panel-legacy {
  opacity: 0.6;
}
.romm-slot-legacy-note {
  font-size: 11px;
  color: #8f98a0;
  font-style: italic;
  padding: 4px 12px 0;
}
/* Last-known slot list — a snapshot from the last contact, not a live list:
   demoted like the legacy bucket and with no pressable header. */
.romm-slot-stale {
  opacity: 0.6;
}
.romm-slot-stale-note {
  font-size: 11px;
  color: #8f98a0;
  font-style: italic;
  margin-bottom: 8px;
}
.romm-slot-stale-detail {
  font-size: 11px;
  color: #8f98a0;
  padding: 0 12px 8px;
}
.romm-slot-header-static {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  background: rgba(255,255,255,0.03);
}
.romm-slot-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  cursor: pointer;
  background: rgba(255,255,255,0.03);
  transition: background 0.15s;
}
.romm-slot-header:hover {
  background: rgba(255,255,255,0.06);
}
.romm-slot-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}
.romm-slot-header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.romm-slot-name {
  font-size: 13px;
  font-weight: 600;
  color: #dcdedf;
}
.romm-slot-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 3px;
  font-weight: 600;
  text-transform: uppercase;
}
.romm-slot-badge-active {
  background: rgba(91,163,43,0.2);
  color: #5ba32b;
}
.romm-slot-badge-server {
  background: rgba(26,159,255,0.15);
  color: #1a9fff;
}
.romm-slot-badge-local {
  background: rgba(212,167,44,0.15);
  color: #d4a72c;
}
.romm-slot-count {
  font-size: 12px;
  color: #8f98a0;
}
.romm-slot-chevron {
  font-size: 14px;
  color: #8f98a0;
  transition: transform 0.2s;
}
.romm-slot-body {
  padding: 8px 12px 12px;
  border-top: 1px solid rgba(255,255,255,0.06);
}
.romm-slot-sync-summary {
  font-size: 12px;
  padding: 4px 12px 0;
}
.romm-save-status-label {
  font-size: 11px;
  font-weight: 600;
}`;
        sp.window.document.head.appendChild(panelStyle);
    }
    if (!sp.window.document.getElementById(ROMM_GEAR_BUTTONS_ID)) {
        const gearStyle = sp.window.document.createElement("style");
        gearStyle.id = ROMM_GEAR_BUTTONS_ID;
        gearStyle.textContent = `
.romm-gear-btn {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 36px !important;
  min-width: 36px !important;
  height: 36px !important;
  border-radius: 4px !important;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.06) !important;
  cursor: pointer;
  transition: background 0.15s ease, filter 0.15s ease;
  padding: 0 !important;
  flex-shrink: 0;
  line-height: normal !important;
}
.romm-gear-btn:hover {
  background: rgba(255,255,255,0.14);
  filter: brightness(1.2);
}
.romm-gear-btn.gpfocus {
  background: rgba(255,255,255,0.14) !important;
  filter: brightness(1.3);
  border-color: rgba(255,255,255,0.5) !important;
}
.romm-gear-btn:active {
  filter: brightness(0.9);
}
.romm-disc-btn {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 7px !important;
  width: auto !important;
  min-width: 0 !important;
  height: 48px !important;
  padding: 0 12px !important;
  border-radius: 2px !important;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.06) !important;
  cursor: pointer;
  transition: background 0.15s ease, filter 0.15s ease;
  flex-shrink: 0;
  line-height: normal !important;
}
.romm-disc-btn:hover {
  background: rgba(255,255,255,0.14);
  filter: brightness(1.2);
}
.romm-disc-btn.gpfocus {
  background: rgba(255,255,255,0.14) !important;
  filter: brightness(1.3);
  border-color: rgba(255,255,255,0.5) !important;
}
.romm-disc-btn:active {
  filter: brightness(0.9);
}
/* Cleanup trash on a vanished version row. The colour lives here rather than on
   the element because Steam repaints a destructive-tone MenuItem red when it
   takes gamepad focus: it flips the row's TEXT to stay legible, but an inline
   icon colour survives that repaint and the red trash disappears into the red
   row. The icon sets no colour prop, so it is fill:currentColor and these rules
   own both states.

   The -row modifier gates the focused colour to the menu row ONLY. The
   singleton binding's trash sits in a .romm-disc-btn whose focus background
   stays dark, so black there would swap one invisible icon for another.

   gpfocus ONLY. Steam marks the focused element itself with gpfocus and its
   ancestors with gpfocuswithin, so this descendant combinator resolves to the
   one focused row. An ancestor-matching pseudo-class must never be used here:
   :focus-within (and :focus on a container) matches every ancestor up to
   <body>, so while the menu is navigated it would repaint EVERY vanished
   row's trash black — at (0,2,0) it also outranks the (0,1,0) red base, so
   the red would never paint on a menu row at all. */
.romm-vanished-trash {
  color: #d94126;
}
.gpfocus .romm-vanished-trash-row {
  color: #000;
}`;
        sp.window.document.head.appendChild(gearStyle);
    }
    if (!sp.window.document.getElementById(ROMM_TABS_ID)) {
        const tabStyle = sp.window.document.createElement("style");
        tabStyle.id = ROMM_TABS_ID;
        tabStyle.textContent = `
.romm-tab-bar {
  display: flex;
  gap: 0;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  padding: 0 2.8vw;
  background: rgba(14, 20, 27, 0.33);
}
.romm-tab {
  padding: 10px 16px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #8f98a0;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: color 0.15s ease, border-color 0.15s ease;
  background: transparent;
  border-top: none;
  border-left: none;
  border-right: none;
  white-space: nowrap;
}
.romm-tab:hover {
  color: #dcdedf !important;
}
.romm-tab.gpfocus,
.romm-tab:focus,
.romm-tab.Focusable.gpfocus {
  color: #dcdedf !important;
  background: rgba(255,255,255,0.06) !important;
  outline: none;
  border-bottom-color: #1a9fff;
}
.romm-tab-active {
  color: #dcdedf !important;
  border-bottom-color: #1a9fff;
}
.romm-tab-content {
  padding: 16px 2.8vw;
  background: rgba(14, 20, 27, 0.33);
}`;
        sp.window.document.head.appendChild(tabStyle);
    }
    if (!sp.window.document.getElementById(ROMM_ACHIEVEMENTS_ID)) {
        const cheevoStyle = sp.window.document.createElement("style");
        cheevoStyle.id = ROMM_ACHIEVEMENTS_ID;
        cheevoStyle.textContent = `
@keyframes romm-gold-sparkle {
  0%, 100% { opacity: 0; transform: scale(0); }
  15% { opacity: 1; transform: scale(1.2); }
  30% { opacity: 0.9; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1); }
  80% { opacity: 0.4; transform: scale(0.6); }
}
.romm-cheevo-badge {
  position: relative;
  cursor: pointer;
}
.romm-cheevo-badge-sparkle {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.romm-sparkle-container {
  position: absolute;
  top: -4px;
  left: -4px;
  right: -4px;
  bottom: -4px;
  pointer-events: none;
  overflow: visible;
}
.romm-sparkle-dot {
  position: absolute;
  width: 2px;
  height: 2px;
  border-radius: 50%;
  background: #fff8dc;
  box-shadow: 0 0 2px 1px #ffd700, 0 0 4px 1px rgba(255, 215, 0, 0.5);
  animation: romm-gold-sparkle var(--romm-sparkle-dur, 2s) ease-in-out infinite;
  animation-delay: var(--romm-sparkle-delay, 0s);
  top: var(--romm-sparkle-top, 50%);
  left: var(--romm-sparkle-left, 50%);
}
.romm-cheevo-trophy {
  color: #ffd700;
  font-size: 14px;
  filter: drop-shadow(0 0 2px rgba(255, 215, 0, 0.5));
}
.romm-cheevo-trophy-none {
  color: #8f98a0;
  font-size: 14px;
  filter: none;
}
.romm-cheevo-count {
  font-size: 13px;
  font-weight: 500;
  color: #dcdedf;
}
.romm-cheevo-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.romm-cheevo-progress-bar {
  height: 6px;
  background: rgba(255,255,255,0.08);
  border-radius: 3px;
  overflow: hidden;
  margin: 8px 0 16px 0;
}
.romm-cheevo-progress-fill {
  height: 100%;
  background: linear-gradient(to right, #ffd700, #ffaa00);
  border-radius: 3px;
  transition: width 0.4s ease-out;
}
.romm-cheevo-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 4px;
  background: rgba(255,255,255,0.03);
  border-left: 3px solid transparent;
}
.romm-cheevo-row-earned {
  background: rgba(255, 215, 0, 0.06);
  border-left-color: #ffd700;
}
.romm-cheevo-img-wrap {
  position: relative;
  flex-shrink: 0;
  width: 48px;
  height: 48px;
}
.romm-cheevo-img-sparkles {
  position: absolute;
  top: -5px;
  left: -5px;
  right: -5px;
  bottom: -5px;
  pointer-events: none;
  overflow: visible;
}
.romm-cheevo-img-sparkle-dot {
  position: absolute;
  width: 2.5px;
  height: 2.5px;
  border-radius: 50%;
  background: #fff8dc;
  box-shadow: 0 0 2px 1px #ffd700, 0 0 5px 1px rgba(255, 215, 0, 0.5);
  animation: romm-gold-sparkle var(--romm-sparkle-dur, 2.5s) ease-in-out infinite;
  animation-delay: var(--romm-sparkle-delay, 0s);
  top: var(--romm-sparkle-top, 50%);
  left: var(--romm-sparkle-left, 50%);
}
.romm-cheevo-badge-img {
  width: 48px;
  height: 48px;
  border-radius: 4px;
  flex-shrink: 0;
  object-fit: cover;
  background: rgba(255,255,255,0.05);
}
.romm-cheevo-details {
  flex: 1;
  min-width: 0;
}
.romm-cheevo-title {
  font-size: 13px;
  font-weight: 600;
  color: #dcdedf;
  line-height: 1.3;
}
.romm-cheevo-desc {
  font-size: 12px;
  color: #8f98a0;
  line-height: 1.4;
  margin-top: 2px;
}
.romm-cheevo-points {
  font-size: 11px;
  color: #ffd700;
  font-weight: 600;
  flex-shrink: 0;
  padding: 2px 8px;
  background: rgba(255, 215, 0, 0.1);
  border-radius: 3px;
}
.romm-cheevo-points-locked {
  color: #8f98a0;
  background: rgba(255,255,255,0.05);
}
.romm-cheevo-earned-label {
  font-size: 10px;
  color: #5ba32b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
}
.romm-cheevo-section-title {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: #8f98a0;
  margin: 12px 0 8px 0;
}
.romm-cheevo-summary {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}
.romm-cheevo-summary-text {
  font-size: 14px;
  font-weight: 600;
  color: #dcdedf;
}
.romm-cheevo-summary-sub {
  font-size: 12px;
  color: #8f98a0;
}
.romm-cheevo-rarity {
  font-size: 10px;
  color: #8f98a0;
  white-space: nowrap;
}
.romm-cheevo-dates {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  flex-shrink: 0;
}
.romm-cheevo-date {
  font-size: 10px;
  color: #8f98a0;
  white-space: nowrap;
  padding: 2px 6px;
  background: rgba(255,255,255,0.06);
  border-radius: 3px;
}
.romm-cheevo-hc-badge {
  display: inline-flex;
  align-items: center;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.5px;
  color: #ffd700;
  padding: 1px 5px;
  background: rgba(255, 215, 0, 0.15);
  border-radius: 3px;
  box-shadow: 0 0 4px rgba(255, 215, 0, 0.3), 0 0 8px rgba(255, 215, 0, 0.15);
  text-shadow: 0 0 4px rgba(255, 215, 0, 0.5);
}
.romm-cheevo-badge-img-hc {
  box-shadow: 0 0 6px rgba(255, 215, 0, 0.4), 0 0 12px rgba(255, 215, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.3);
}`;
        sp.window.document.head.appendChild(cheevoStyle);
    }
}
function showNativePlaySection() {
    const sp = findSP();
    if (!sp?.window.document)
        return;
    sp.window.document.getElementById(ROMM_PLAY_HIDE_ID)?.remove();
    sp.window.document.getElementById(ROMM_FOCUS_STYLES_ID)?.remove();
    sp.window.document.getElementById(ROMM_INFO_ITEMS_ID)?.remove();
    sp.window.document.getElementById(ROMM_GAME_INFO_PANEL_ID)?.remove();
    sp.window.document.getElementById(ROMM_GEAR_BUTTONS_ID)?.remove();
    sp.window.document.getElementById(ROMM_TABS_ID)?.remove();
    sp.window.document.getElementById(ROMM_ACHIEVEMENTS_ID)?.remove();
}

function hasAnySaveConflict(status) {
    return (status?.conflicts?.length ?? 0) > 0;
}

let _state$4 = "checking";
const connectionListeners = new Set();
function getRommConnectionState() {
    return _state$4;
}
function setRommConnectionState(s, reason = "unspecified") {
    if (_state$4 === s)
        return;
    const previous = _state$4;
    _state$4 = s;
    detach(debugLog(`connectionState: ${previous} -> ${s} (${reason})`));
    connectionListeners.forEach((l) => l(s));
}
function reportServerReachable(ok) {
    setRommConnectionState(ok ? "connected" : "offline", "reachability report");
}
function onRommConnectionChange(cb) {
    connectionListeners.add(cb);
    return () => {
        connectionListeners.delete(cb);
    };
}
function useRommConnectionState() {
    const [state, setState] = SP_REACT.useState(getRommConnectionState());
    SP_REACT.useEffect(() => onRommConnectionChange(setState), []);
    return state;
}
let _retryProgress = null;
let _retryProgressGeneration = 0;
let _loadGeneration = 0;
const retryProgressListeners = new Set();
function getServerRetryProgress() {
    return _retryProgress;
}
function setServerRetryProgress(p) {
    if (p === null) {
        if (_retryProgress === null)
            return;
        _retryProgress = null;
    }
    else {
        const shown = _retryProgress;
        if (shown !== null && _retryProgressGeneration === _loadGeneration && p.attempt < shown.attempt)
            return;
        _retryProgress = p;
        _retryProgressGeneration = _loadGeneration;
    }
    retryProgressListeners.forEach((l) => l(_retryProgress));
}
function onServerRetryProgressChange(cb) {
    retryProgressListeners.add(cb);
    return () => {
        retryProgressListeners.delete(cb);
    };
}
function beginServerLoad() {
    _loadGeneration += 1;
    return { generation: _loadGeneration };
}
function settleServerLoad(token) {
    if (token.generation === _loadGeneration)
        setServerRetryProgress(null);
}
function useServerRetryProgress() {
    const [progress, setProgress] = SP_REACT.useState(getServerRetryProgress());
    SP_REACT.useEffect(() => onServerRetryProgressChange(setProgress), []);
    return progress;
}
let _versionError = null;
const versionErrorListeners = new Set();
function getVersionError() {
    return _versionError;
}
function setVersionError(msg) {
    if (_versionError === msg)
        return;
    _versionError = msg;
    versionErrorListeners.forEach((l) => l(msg));
}
function onVersionErrorChange(cb) {
    versionErrorListeners.add(cb);
    return () => {
        versionErrorListeners.delete(cb);
    };
}

const vanishedAppIds = new Map();
const listeners$2 = new Set();
function setBoundVanished(appId, vanished) {
    if ((vanishedAppIds.get(appId) ?? false) === vanished)
        return;
    vanishedAppIds.set(appId, vanished);
    for (const listener of listeners$2)
        listener();
}
function isBoundVanished(appId) {
    return vanishedAppIds.get(appId) ?? false;
}
function onBoundVanishedChange(listener) {
    listeners$2.add(listener);
    return () => listeners$2.delete(listener);
}

function offsetWithinScroller(el, scroller) {
    const elTop = el.getBoundingClientRect().top;
    const scrollerTop = scroller.getBoundingClientRect().top;
    return elTop - scrollerTop - scroller.clientTop + scroller.scrollTop;
}
function findScrollParent(el) {
    let parent = el.parentElement;
    while (parent) {
        const ov = globalThis.getComputedStyle(parent).overflowY;
        if ((ov === "scroll" || ov === "auto") && parent.scrollHeight > parent.clientHeight)
            return parent;
        parent = parent.parentElement;
    }
    return null;
}
function findOutermostScrollParent(el) {
    let parent = el.parentElement;
    let outermost = null;
    while (parent) {
        const ov = globalThis.getComputedStyle(parent).overflowY;
        if ((ov === "scroll" || ov === "auto") && parent.scrollHeight > parent.clientHeight)
            outermost = parent;
        parent = parent.parentElement;
    }
    return outermost;
}
function scrollFocusedToCenter(e) {
    const el = e.currentTarget;
    setTimeout(() => {
        if (!el)
            return;
        const scrollParent = findScrollParent(el);
        if (scrollParent) {
            const elRect = el.getBoundingClientRect();
            const spRect = scrollParent.getBoundingClientRect();
            const targetScroll = scrollParent.scrollTop + (elRect.top - spRect.top) - spRect.height / 2 + elRect.height / 2;
            scrollParent.scrollTo({ top: targetScroll, behavior: "smooth" });
        }
    }, 50);
}
function scrollNearestToTop(e) {
    const el = e.currentTarget;
    setTimeout(() => {
        if (!el)
            return;
        findScrollParent(el)?.scrollTo({ top: 0, behavior: "smooth" });
    }, 50);
}
function scrollToTop(e) {
    const el = e.currentTarget;
    setTimeout(() => {
        if (!el)
            return;
        const scrollParent = findOutermostScrollParent(el);
        if (scrollParent) {
            scrollParent.scrollTo({ top: 0, behavior: "smooth" });
        }
    }, 50);
}
const SCROLL_TOP_MARGIN_FRACTION = 0.1;
const SCROLL_TOP_MARGIN_CAP = 120;
function scrollElementToTop(el) {
    setTimeout(() => {
        if (!el)
            return;
        const scrollParent = findOutermostScrollParent(el);
        if (!scrollParent)
            return;
        const topMargin = Math.min(SCROLL_TOP_MARGIN_CAP, scrollParent.clientHeight * SCROLL_TOP_MARGIN_FRACTION);
        const elRect = el.getBoundingClientRect();
        const spRect = scrollParent.getBoundingClientRect();
        const targetScroll = scrollParent.scrollTop + (elRect.top - spRect.top) - topMargin;
        scrollParent.scrollTo({ top: Math.max(0, targetScroll), behavior: "auto" });
    }, 50);
}

function getEventTarget(e) {
    return (e.currentTarget ?? e.target);
}

function resolveSaveSetupOutcome(info) {
    if (info.recommended_action === "server_unreachable") {
        return { kind: "server_unreachable" };
    }
    if (info.recommended_action === "not_found") {
        return { kind: "not_found" };
    }
    if (info.recommended_action === "auto_confirm_default") {
        return { kind: "auto_confirm", slot: info.default_slot };
    }
    if (info.recommended_action === "auto_adopt_server") {
        return { kind: "auto_confirm", slot: info.auto_slot ?? info.default_slot };
    }
    if (info.server_slots.length === 0) {
        return { kind: "auto_confirm", slot: info.default_slot };
    }
    return { kind: "needs_user_choice" };
}
const SERVER_UNREACHABLE_WIZARD_MESSAGE = "RomM server is not reachable — cannot configure save slot. Retry once the server is back.";
const SERVER_UNREACHABLE_TOAST_BODY = "Cannot configure save slot — RomM server is not reachable. Open the Saves tab to retry.";
const NOT_FOUND_WIZARD_MESSAGE = "RomM couldn't find the save data for this setup — setup paused. The game or this device may no longer be on the server.";
const NOT_FOUND_TOAST_BODY = "Cannot configure save slot — RomM couldn't find the save data for this setup. Open the Saves tab.";
const NEEDS_USER_CHOICE_TOAST_BODY = "Configure save sync in the Saves tab first";
const CONFIRM_FAILED_TOAST_BODY = "Couldn't configure save sync — open the Saves tab to finish setup.";
async function applyLaunchGateSetupOutcome(outcome, deps) {
    if (outcome.kind === "server_unreachable") {
        deps.toast(SERVER_UNREACHABLE_TOAST_BODY);
        deps.dispatchSavesTab();
        return "abort";
    }
    if (outcome.kind === "not_found") {
        deps.toast(NOT_FOUND_TOAST_BODY);
        deps.dispatchSavesTab();
        return "abort";
    }
    if (outcome.kind === "auto_confirm") {
        const result = await deps.confirmSlotChoice(deps.rid, outcome.slot, false, null, false);
        if (result?.success === false) {
            deps.toast(result.message || CONFIRM_FAILED_TOAST_BODY);
            deps.dispatchSavesTab();
            return "abort";
        }
        return "proceed";
    }
    deps.toast(NEEDS_USER_CHOICE_TOAST_BODY);
    deps.dispatchSavesTab();
    return "abort";
}
async function applyWizardInitialSetupResult(result, deps) {
    if (result.recommended_action === "server_unreachable") {
        deps.setError(SERVER_UNREACHABLE_WIZARD_MESSAGE);
        return;
    }
    if (result.recommended_action === "not_found") {
        deps.setError(NOT_FOUND_WIZARD_MESSAGE);
        return;
    }
    if (result.recommended_action === "auto_confirm_default") {
        deps.setConfirming(true);
        try {
            const confirmResult = await deps.confirmSlotChoice(deps.romId, result.default_slot, false, null, false);
            if (deps.isCancelled())
                return;
            if (confirmResult?.success === false) {
                deps.setError(`Auto-setup failed: ${confirmResult.message || "could not confirm slot"}`);
                deps.logError(`SlotSetupWizard auto-confirm returned success=false: ${confirmResult.message ?? ""}`);
                deps.setConfirming(false);
                deps.setInfo(result);
                return;
            }
            deps.onComplete();
        }
        catch (e) {
            if (!deps.isCancelled()) {
                deps.setError(`Auto-setup failed: ${e}`);
                deps.logError(`SlotSetupWizard auto-confirm failed: ${e}`);
                deps.setConfirming(false);
                deps.setInfo(result);
            }
        }
        return;
    }
    deps.setInfo(result);
}
function applyWizardRetrySetupResult(result, deps) {
    if (result.recommended_action === "server_unreachable") {
        deps.setError(SERVER_UNREACHABLE_WIZARD_MESSAGE);
        deps.setLoading(false);
        return;
    }
    if (result.recommended_action === "not_found") {
        deps.setError(NOT_FOUND_WIZARD_MESSAGE);
        deps.setLoading(false);
        return;
    }
    deps.setInfo(result);
    deps.setLoading(false);
}
function legacyTrackExplainer(slot) {
    return `Tracking copies the legacy save into ‘${slot}’ — the legacy save itself is left untouched in the read-only legacy bucket.`;
}
function legacyConflictReplaceNotice(slot) {
    return `Your local save is moved to .romm-backup and replaced with the legacy save. Cancel to go back — nothing changes, and you can start fresh with ‘${slot}’ instead.`;
}
function legacyMigrateConfirmDescription(slot) {
    return `Copy the legacy save into ‘${slot}’? If a local save differs, you’ll confirm before anything is replaced.`;
}
function startFreshHint(slot) {
    return `Your local save becomes the first save in ‘${slot}’ on the next sync.`;
}
function startFreshHintNewSlot() {
    return "Your local save becomes the first save in the new slot on the next sync.";
}
function wizardMigrationOutcomeToastBody(migrated, failed, slot) {
    const legacyNote = migrated === 1
        ? " The legacy save stays in the read-only legacy bucket."
        : " The legacy saves stay in the read-only legacy bucket.";
    if (migrated > 0 && failed > 0) {
        return `Migrated ${migrated} save${migrated === 1 ? "" : "s"} into ‘${slot}’; ${failed} could not be migrated.${legacyNote}`;
    }
    if (migrated > 0) {
        return `Migrated ${migrated} save${migrated === 1 ? "" : "s"} into ‘${slot}’.${legacyNote}`;
    }
    if (failed > 0) {
        return `Could not migrate ${failed} save${failed === 1 ? "" : "s"} into ‘${slot}’`;
    }
    return null;
}

function handleGlobalDownloadFailure(event, store, toast) {
    const prev = store.getDownloadState().find((d) => d.rom_id === event.rom_id);
    store.updateDownload({
        rom_id: event.rom_id,
        rom_name: event.rom_name,
        platform_name: event.platform_name,
        file_name: prev?.file_name ?? "",
        status: "failed",
        progress: prev?.progress ?? 0,
        bytes_downloaded: prev?.bytes_downloaded ?? 0,
        total_bytes: prev?.total_bytes ?? 0,
        resumable: prev?.resumable ?? false,
        error: event.error_message,
    });
    toast.toast({
        title: PLUGIN_NAME,
        body: `Download failed: ${event.rom_name} — ${event.error_message}`,
    });
}
function handleButtonDownloadFailure(event, romId, reset) {
    if (romId === null || event.rom_id !== romId)
        return;
    reset();
}

const LABEL_STYLE$4 = { fontSize: "12px", color: "rgba(255,255,255,0.55)" };
const VALUE_STYLE = { fontSize: "13px", color: "#fff" };
function formatTimestamp$1(epochSeconds) {
    if (!epochSeconds)
        return "";
    return new Date(epochSeconds * 1000).toLocaleString();
}
function nounFor(occupied) {
    const kind = occupied.existing.kind;
    return kind === null ? "thing" : ENTRY_KIND_LABEL[kind];
}
function describesTheGame(occupied) {
    return occupied.existing.kind === "file" || occupied.existing.kind === "dir";
}
function existingSize(occupied, candidate) {
    if (candidate && occupied.existing.kind === "dir")
        return "Folder — not measured";
    if (occupied.existing.kind === "link")
        return "Shortcut — no size of its own";
    if (occupied.existing.kind === null)
        return "No size to show";
    return formatBytes$1(occupied.existing.size_bytes);
}
function sizeVerdict(occupied, candidate) {
    if (candidate && occupied.existing.kind === "dir") {
        return "Folders are not measured before you open this, so the two sizes are not compared.";
    }
    if (occupied.existing.kind === "link") {
        return "A shortcut is not the game's bytes, so there is nothing here to compare.";
    }
    if (occupied.existing.kind === null)
        return "This is not a file or a folder, so there is nothing here to compare.";
    if (occupied.sizes_match === null)
        return "The server did not state a size, so the two cannot be compared.";
    if (occupied.sizes_match)
        return "Both are the same size.";
    const delta = occupied.existing.size_bytes - occupied.incoming.size_bytes;
    return delta > 0
        ? `What is here is ${formatBytes$1(delta)} larger than what the server would send.`
        : `What is here is ${formatBytes$1(-delta)} smaller than what the server would send.`;
}
function replaceWarning(occupied, candidate, noun) {
    const name = occupied.existing.name;
    if (occupied.existing.kind === "link") {
        return `Downloading deletes the shortcut that is here now — ${name}. Whatever it points at is left alone. Continue?`;
    }
    if (occupied.existing.kind === null) {
        return `Downloading removes what is here now — ${name}. Arcoon Deck cannot tell what it is, only that it goes. Continue?`;
    }
    return (`Downloading deletes the ${noun} that is here now — ${name}, ${existingSize(occupied, candidate)}. ` +
        "If it is your own dump, patch or romhack, it is gone. Continue?");
}
const VERIFY_COLORS = {
    match: "#6dd36d",
    mismatch: "#ff8a80",
    unverifiable: "rgba(255,255,255,0.7)",
    missing: "#ff8a80",
    error: "#ff8a80",
};
const AdoptExistingModal = ({ romId, occupied, candidatePath, closeModal, onChoice, }) => {
    const [verifying, setVerifying] = SP_REACT.useState(false);
    const [verifyProgress, setVerifyProgress] = SP_REACT.useState(null);
    const [verdict, setVerdict] = SP_REACT.useState(null);
    const [confirmingReplace, setConfirmingReplace] = SP_REACT.useState(false);
    SP_REACT.useEffect(() => {
        const listener = addEventListener("verify_progress", (payload) => {
            if (payload.rom_id !== romId || !payload.bytes_total)
                return;
            setVerifyProgress(payload.bytes_done / payload.bytes_total);
        });
        return () => removeEventListener("verify_progress", listener);
    }, [romId]);
    const handleVerify = async () => {
        if (verifying)
            return;
        setVerifying(true);
        setVerdict(null);
        setVerifyProgress(0);
        try {
            setVerdict(await verifyExistingContent(romId, candidatePath ?? null));
        }
        catch (e) {
            detach(debugLog(`AdoptExistingModal: verify failed: ${e}`));
            setVerdict({ status: "error", message: "Couldn't reach the server to check these files", differences: [] });
        }
        finally {
            setVerifying(false);
            setVerifyProgress(null);
        }
    };
    const choose = (choice) => {
        closeModal?.();
        onChoice(choice);
    };
    const noun = nounFor(occupied);
    const modified = formatTimestamp$1(occupied.existing.modified_at);
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: closeModal, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "420px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "16px", fontWeight: "bold", color: "#fff", marginBottom: "4px" }, children: "This Game Is Already on Your Device" }), SP_JSX.jsx("div", { style: { fontSize: "13px", color: "rgba(255,255,255,0.7)", marginBottom: "12px" }, children: candidatePath
                        ? `This ${noun} carries this game's name. Arcoon Deck did not put it there, so it will not be touched until ` +
                            "you decide."
                        : `A ${noun} is already where this game would be downloaded. Arcoon Deck did not put it there, so it will not ` +
                            "be touched until you decide." }), SP_JSX.jsxs("div", { style: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "8px" }, children: [SP_JSX.jsxs("div", { children: [SP_JSX.jsx("div", { style: LABEL_STYLE$4, children: "On this device" }), SP_JSX.jsx("div", { style: VALUE_STYLE, children: occupied.existing.name }), SP_JSX.jsx("div", { style: VALUE_STYLE, children: existingSize(occupied, Boolean(candidatePath)) }), modified && describesTheGame(occupied) && SP_JSX.jsxs("div", { style: LABEL_STYLE$4, children: ["Last changed ", modified] })] }), SP_JSX.jsxs("div", { children: [SP_JSX.jsx("div", { style: LABEL_STYLE$4, children: "On the server" }), SP_JSX.jsx("div", { style: VALUE_STYLE, children: occupied.incoming.name }), SP_JSX.jsx("div", { style: VALUE_STYLE, children: occupied.incoming.size_bytes ? formatBytes$1(occupied.incoming.size_bytes) : "Size unknown" })] })] }), SP_JSX.jsx("div", { style: { fontSize: "13px", color: "#fff", marginBottom: "12px" }, children: sizeVerdict(occupied, Boolean(candidatePath)) }), candidatePath && (SP_JSX.jsxs("div", { style: { fontSize: "13px", color: "rgba(255,255,255,0.7)", marginBottom: "12px" }, children: ["Using it renames it to ", occupied.incoming.name, ", and moves any saves and savestates named after it with it, so this game works the same as one Arcoon Deck downloaded."] })), verifying && (SP_JSX.jsx("div", { style: { fontSize: "13px", color: "rgba(255,255,255,0.7)", marginBottom: "12px" }, children: verifyProgress === null || verifyProgress === 0
                        ? "Checking the files…"
                        : `Checking the files… ${Math.round(verifyProgress * 100)}%` })), !verifying && verdict && (SP_JSX.jsxs("div", { style: { marginBottom: "12px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "13px", color: VERIFY_COLORS[verdict.status] }, children: verdict.message }), verdict.differences.map((d) => (SP_JSX.jsxs("div", { style: { ...LABEL_STYLE$4, marginTop: "4px" }, children: [d.name, ": ", d.detail] }, d.name)))] })), confirmingReplace ? (SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "13px", color: "#ff8a80" }, children: replaceWarning(occupied, Boolean(candidatePath), noun) }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose("replace"), children: "Delete and Download" }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => setConfirmingReplace(false), style: { opacity: 0.5 }, children: "Go Back" })] })) : (SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: [SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose("adopt"), disabled: !occupied.adoptable, children: occupied.adoptable ? "Use These Files" : `Can't use this ${noun} for this game` }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => {
                                detach(handleVerify());
                            }, disabled: verifying, children: "Check Against Server" }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => setConfirmingReplace(true), children: "Download Instead" }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose("cancel"), style: { opacity: 0.5 }, children: "Cancel" })] }))] }) }));
};
function showAdoptExistingModal(romId, occupied, candidatePath) {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(AdoptExistingModal, { romId: romId, occupied: occupied, candidatePath: candidatePath, onChoice: resolve }));
    });
}
function comparisonForCandidate(candidate, incoming) {
    return {
        success: false,
        reason: "target_occupied",
        message: `'${candidate.name}' is already on this device`,
        existing: {
            name: candidate.name,
            path: candidate.path,
            kind: candidate.is_dir ? "dir" : "file",
            size_bytes: candidate.size_bytes,
            modified_at: candidate.modified_at,
        },
        incoming,
        sizes_match: candidate.is_dir || !incoming.size_bytes ? null : candidate.size_bytes === incoming.size_bytes,
        adoptable: true,
    };
}

const LABEL_STYLE$3 = { fontSize: "12px", color: "rgba(255,255,255,0.55)" };
const AdoptCandidateModal = ({ found, closeModal, onChoice }) => {
    const choose = (choice) => {
        closeModal?.();
        onChoice(choice);
    };
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: closeModal, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "420px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "16px", fontWeight: "bold", color: "#fff", marginBottom: "4px" }, children: "This Game May Already Be on Your Device" }), SP_JSX.jsx("div", { style: { fontSize: "13px", color: "rgba(255,255,255,0.7)", marginBottom: "12px" }, children: "These files sit in the same folder and carry this game's name. Arcoon Deck did not put them there, so nothing is touched until you pick one." }), SP_JSX.jsx("div", { style: { display: "flex", flexDirection: "column", gap: "8px", marginBottom: "12px" }, children: found.candidates.map((candidate) => (SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose({ kind: "candidate", candidate }), children: SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", alignItems: "flex-start" }, children: [SP_JSX.jsx("div", { style: { fontSize: "13px", color: "#fff" }, children: candidate.name }), SP_JSX.jsxs("div", { style: LABEL_STYLE$3, children: [candidate.detail, candidate.is_dir ? " — folder" : ` — ${formatBytes$1(candidate.size_bytes)}`] })] }) }, candidate.path))) }), found.truncated && (SP_JSX.jsxs("div", { style: { ...LABEL_STYLE$3, marginBottom: "12px" }, children: ["Only the ", found.candidates.length, " strongest matches are shown \u2014 there are more in this folder."] })), SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: [SP_JSX.jsxs(DFL.DialogButton, { onClick: () => choose({ kind: "download" }), children: ["None of These \u2014 Download ", found.incoming.name] }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose({ kind: "cancel" }), style: { opacity: 0.5 }, children: "Cancel" })] })] }) }));
};
function showAdoptCandidateModal(found) {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(AdoptCandidateModal, { found: found, onChoice: resolve }));
    });
}

const LABEL_STYLE$2 = { fontSize: "12px", color: "rgba(255,255,255,0.55)" };
const KIND_LABEL = {
    rom: "game file",
    save: "save",
    savestate: "savestate",
};
const AdoptCollisionModal = ({ collisions, closeModal, onChoice }) => {
    const choose = (choice) => {
        closeModal?.();
        onChoice(choice);
    };
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: closeModal, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "420px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "16px", fontWeight: "bold", color: "#fff", marginBottom: "4px" }, children: "Some of These Names Are Taken" }), SP_JSX.jsx("div", { style: { fontSize: "13px", color: "rgba(255,255,255,0.7)", marginBottom: "12px" }, children: "Moving this game's files to the name your server uses would land on files that already exist. Nothing has been moved yet." }), SP_JSX.jsx("div", { style: { marginBottom: "12px" }, children: collisions.map((collision) => (SP_JSX.jsxs("div", { style: { fontSize: "13px", color: "#fff", marginBottom: "2px" }, children: [collision.name, " ", SP_JSX.jsxs("span", { style: LABEL_STYLE$2, children: ["(", KIND_LABEL[collision.kind], ")"] })] }, collision.path))) }), SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: [SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose("overwrite"), children: "Replace Them" }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose("keep"), children: "Keep Them" }), SP_JSX.jsx("div", { style: LABEL_STYLE$2, children: "Replace does not delete the files listed above \u2014 each is moved into a .romm-backup folder beside it, so you can put one back by hand if you pick wrong. Keep leaves them alone and leaves this game's old-named saves where they are \u2014 nothing is lost, but nothing will be reading them either." }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose("cancel"), style: { opacity: 0.5 }, children: "Cancel" })] })] }) }));
};
function showAdoptCollisionModal(collisions) {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(AdoptCollisionModal, { collisions: collisions, onChoice: resolve }));
    });
}

const LABEL_STYLE$1 = { fontSize: "12px", color: "rgba(255,255,255,0.55)" };
const AdoptUnusableModal = ({ unusable, closeModal, onChoice }) => {
    const choose = (choice) => {
        closeModal?.();
        onChoice(choice);
    };
    const servedWord = unusable.served_is_dir ? "a folder of several files" : "a single file";
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: closeModal, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "420px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "16px", fontWeight: "bold", color: "#fff", marginBottom: "4px" }, children: "Something With This Name Is Already Here" }), SP_JSX.jsxs("div", { style: { fontSize: "13px", color: "rgba(255,255,255,0.7)", marginBottom: "12px" }, children: ["Your server sends this game as ", servedWord, ", and what is in this folder is not something Arcoon Deck can use as this game. Downloading leaves you with two copies \u2014 the one below, and the one it fetches."] }), SP_JSX.jsx("div", { style: { marginBottom: "12px" }, children: unusable.existing.map((entry) => (SP_JSX.jsxs("div", { style: { fontSize: "13px", color: "#fff", marginBottom: "2px" }, children: [entry.name, " ", SP_JSX.jsxs("span", { style: LABEL_STYLE$1, children: ["(", ENTRY_KIND_LABEL[entry.kind], ")"] })] }, entry.path))) }), unusable.truncated && (SP_JSX.jsxs("div", { style: { ...LABEL_STYLE$1, marginBottom: "12px" }, children: ["Only the first ", unusable.existing.length, " are shown \u2014 there are more in this folder."] })), SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: [SP_JSX.jsxs(DFL.DialogButton, { onClick: () => choose("download"), children: ["Download ", unusable.incoming.name, " Anyway"] }), SP_JSX.jsx("div", { style: LABEL_STYLE$1, children: "Nothing above is renamed, moved or deleted \u2014 the download lands beside it under your server's name." }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose("cancel"), style: { opacity: 0.5 }, children: "Cancel" })] })] }) }));
};
function showAdoptUnusableModal(unusable) {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(AdoptUnusableModal, { unusable: unusable, onChoice: resolve }));
    });
}

const LABEL_STYLE = { fontSize: "12px", color: "rgba(255,255,255,0.55)" };
const AdoptVanishedModal = ({ vanished, closeModal, onChoice }) => {
    const choose = (choice) => {
        closeModal?.();
        onChoice(choice);
    };
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: closeModal, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "420px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "16px", fontWeight: "bold", color: "#fff", marginBottom: "4px" }, children: "The Copy on This Device Cannot Be Found" }), SP_JSX.jsx("div", { style: { fontSize: "13px", color: "rgba(255,255,255,0.7)", marginBottom: "12px" }, children: "This game's page found a copy on this device, and looking again now turns up nothing that matches. Nothing has been changed on your device." }), SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: [SP_JSX.jsxs(DFL.DialogButton, { onClick: () => choose("download"), children: ["Download ", vanished.incoming.name] }), SP_JSX.jsx("div", { style: LABEL_STYLE, children: "Or cancel and look in the folder yourself first." }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => choose("cancel"), style: { opacity: 0.5 }, children: "Cancel" })] })] }) }));
};
function showAdoptVanishedModal(vanished) {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(AdoptVanishedModal, { vanished: vanished, onChoice: resolve }));
    });
}

const CoreChangeModalContent = ({ oldLabel, newLabel, closeModal, onDone }) => {
    const handleChoice = (proceed) => {
        closeModal?.();
        onDone(proceed);
    };
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: () => {
            closeModal?.();
            onDone(false);
        }, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "320px" }, children: [SP_JSX.jsx("div", { style: {
                        fontSize: "16px",
                        fontWeight: "bold",
                        marginBottom: "4px",
                        color: "#fff",
                    }, children: "Emulator Core Changed" }), SP_JSX.jsxs("div", { style: {
                        fontSize: "13px",
                        color: "rgba(255, 255, 255, 0.6)",
                        marginBottom: "16px",
                    }, children: [oldLabel, " \u2192 ", newLabel] }), SP_JSX.jsxs("div", { style: {
                        padding: "10px",
                        background: "rgba(255, 152, 0, 0.15)",
                        borderRadius: "4px",
                        border: "1px solid rgba(255, 152, 0, 0.3)",
                        marginBottom: "12px",
                    }, children: [SP_JSX.jsx("div", { style: { fontSize: "12px", color: "#ffb74d", marginBottom: "6px", fontWeight: "bold" }, children: "Save Compatibility Warning" }), SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", lineHeight: "1.4" }, children: "Some emulator cores use incompatible save formats. Continuing may overwrite your existing saves with data the previous core can't read." })] }), SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: [SP_JSX.jsx(DFL.DialogButton, { onClick: () => handleChoice(true), children: "Continue" }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => handleChoice(false), style: { opacity: 0.5 }, children: "Cancel" })] })] }) }));
};
function showCoreChangeModal(oldLabel, newLabel) {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(CoreChangeModalContent, { oldLabel: oldLabel, newLabel: newLabel, onDone: resolve }));
    });
}

function formatSize$1(bytes) {
    if (bytes == null || bytes === 0)
        return "unknown";
    return formatBytes$1(bytes);
}
const SyncConflictModal = ({ conflict, onResolve, onCancel, isLoading = false, errorMessage = null, }) => {
    const handleResolve = (action) => {
        onResolve(action).catch(() => {
        });
    };
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: isLoading ? undefined : onCancel, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "360px" }, children: [SP_JSX.jsxs("div", { style: {
                        fontSize: "16px",
                        fontWeight: "bold",
                        marginBottom: "4px",
                        color: "#fff",
                    }, children: ["Save conflict for ", conflict.filename] }), SP_JSX.jsx("div", { style: {
                        fontSize: "12px",
                        color: "rgba(255, 255, 255, 0.6)",
                        marginBottom: "16px",
                        lineHeight: "1.4",
                    }, children: "Both your local save and the server save have changed since the last sync. Pick which version to keep \u2014 the other will be overwritten." }), SP_JSX.jsxs("div", { style: {
                        padding: "10px",
                        background: "rgba(76, 175, 80, 0.15)",
                        borderRadius: "4px",
                        border: "1px solid rgba(76, 175, 80, 0.3)",
                        marginBottom: "10px",
                    }, children: [SP_JSX.jsx("div", { style: { fontSize: "12px", fontWeight: "bold", color: "#81c784", marginBottom: "6px" }, children: "Your local save" }), SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "2px" }, children: [formatSize$1(conflict.local_size), " \u00B7 modified ", formatTimestamp$2(conflict.local_mtime)] }), SP_JSX.jsx("div", { style: { marginTop: "8px" }, children: SP_JSX.jsx(DFL.DialogButton, { onClick: () => handleResolve("keep_local"), disabled: isLoading, children: "Keep Local" }) })] }), SP_JSX.jsxs("div", { style: {
                        padding: "10px",
                        background: "rgba(33, 150, 243, 0.15)",
                        borderRadius: "4px",
                        border: "1px solid rgba(33, 150, 243, 0.3)",
                        marginBottom: "10px",
                    }, children: [SP_JSX.jsxs("div", { style: { fontSize: "12px", fontWeight: "bold", color: "#64b5f6", marginBottom: "6px" }, children: ["Server save (id=", conflict.server_save_id, ")"] }), SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "2px" }, children: [formatSize$1(conflict.server_size), " \u00B7 uploaded ", formatTimestamp$2(conflict.server_updated_at)] }), SP_JSX.jsx("div", { style: { marginTop: "8px" }, children: SP_JSX.jsx(DFL.DialogButton, { onClick: () => handleResolve("use_server"), disabled: isLoading, children: "Use Server" }) })] }), errorMessage ? (SP_JSX.jsx("div", { style: {
                        padding: "8px 10px",
                        background: "rgba(244, 67, 54, 0.15)",
                        borderRadius: "4px",
                        border: "1px solid rgba(244, 67, 54, 0.3)",
                        marginBottom: "12px",
                        fontSize: "12px",
                        color: "#ef9a9a",
                        lineHeight: "1.4",
                    }, children: errorMessage })) : null, SP_JSX.jsx("div", { style: { display: "flex", justifyContent: "flex-end" }, children: SP_JSX.jsx(DFL.DialogButton, { onClick: onCancel, disabled: isLoading, style: { opacity: 0.7 }, children: "Cancel" }) })] }) }));
};
const SyncConflictModalHost = ({ conflict, closeModal, onDone }) => {
    const [isLoading, setIsLoading] = SP_REACT.useState(false);
    const [errorMessage, setErrorMessage] = SP_REACT.useState(null);
    const handleResolve = async (action) => {
        setIsLoading(true);
        setErrorMessage(null);
        try {
            const result = await resolveSyncConflict(conflict.rom_id, conflict.filename, conflict.server_save_id, action);
            if (!result.success) {
                if (result.reason === "stale_conflict") {
                    const staleMsg = "The server save has been updated by another device. Please cancel and retry sync to get the latest version.";
                    logError(`resolveSyncConflict(${conflict.rom_id}, ${conflict.filename}, ${action}) stale: ${result.message ?? ""}`);
                    setErrorMessage(staleMsg);
                    setIsLoading(false);
                    return;
                }
                const msg = result.message ?? "Failed to resolve conflict";
                logError(`resolveSyncConflict(${conflict.rom_id}, ${conflict.filename}, ${action}) failed: ${msg}`);
                setErrorMessage(msg);
                setIsLoading(false);
                return;
            }
            const successBody = action === "keep_local"
                ? "Conflict resolved — kept your local save (uploaded to server)."
                : "Conflict resolved — used the server save · your local was backed up.";
            showToast(successBody);
            closeModal?.();
            onDone(action);
        }
        catch (e) {
            const msg = e instanceof Error ? e.message : String(e);
            logError(`resolveSyncConflict(${conflict.rom_id}, ${conflict.filename}, ${action}) threw: ${msg}`);
            setErrorMessage(msg || "Failed to resolve conflict");
            setIsLoading(false);
        }
    };
    const handleCancel = () => {
        if (isLoading)
            return;
        closeModal?.();
        onDone("cancel");
    };
    return (SP_JSX.jsx(SyncConflictModal, { conflict: conflict, onResolve: handleResolve, onCancel: handleCancel, isLoading: isLoading, errorMessage: errorMessage }));
};
function showSyncConflictModal(conflict) {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(SyncConflictModalHost, { conflict: conflict, onDone: resolve }));
    });
}
async function handleConflicts(conflicts) {
    for (const conflict of conflicts) {
        const resolution = await showSyncConflictModal(conflict);
        if (resolution === "cancel")
            return "cancel";
    }
    return "resolved";
}

function showOfflineDriftModal() {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "RomM Unreachable", strDescription: "Your local save has unsynced changes. Playing now may create a conflict you'll resolve later. Start anyway?", strOKButtonText: "Start Anyway", strMiddleButtonText: "Retry connection", strCancelButtonText: "Cancel", onOK: () => resolve("start_anyway"), onMiddleButton: () => resolve("retry"), onCancel: () => resolve("cancel") }));
    });
}

function showFallbackLaunchModal(message) {
    const description = message?.trim()
        ? `${message} — launch with local saves?`
        : "Couldn't sync saves with RomM server. Launch with local saves?";
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Save Sync Unavailable", strDescription: description, strOKButtonText: "Launch Anyway", strCancelButtonText: "Cancel", onOK: () => resolve(true), onCancel: () => resolve(false) }));
    });
}

function showStopGameModal() {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Stop Game?", strDescription: "Any progress since the last in-game save may be lost.", strOKButtonText: "Stop Game", strCancelButtonText: "Cancel", onOK: () => resolve(true), onCancel: () => resolve(false) }));
    });
}

async function runLaunchGate(_appId, _romId, ops) {
    try {
        if (ops.migrationPending()) {
            return { decision: "block", reason: "migration_pending" };
        }
        if (!(await ops.hasLaunchTarget())) {
            return { decision: "block", reason: "no_launch_target" };
        }
        if ((await ops.ensureTrackingConfigured()) === "abort") {
            return { decision: "abort" };
        }
        if (!(await ops.checkCoreChange())) {
            return { decision: "abort" };
        }
        const online = await ops.checkReachability();
        if (online) {
            const sync = await ops.preLaunchSync();
            if (sync.conflicts && sync.conflicts.length > 0) {
                return { decision: "conflict", conflicts: sync.conflicts };
            }
            if (!sync.success) {
                return { decision: "sync_failed", message: sync.message };
            }
            return { decision: "allow" };
        }
        if (await ops.checkLocalDrift()) {
            return { decision: "offline_drift" };
        }
        return { decision: "allow" };
    }
    catch (e) {
        logError(`runLaunchGate threw (failing open to allow): ${e}`);
        return { decision: "allow" };
    }
}
const _skip = new Set();
function markLaunchSkipped(appId) {
    _skip.add(appId);
}
function consumeLaunchSkip(appId) {
    return _skip.delete(appId);
}

const NO_LAUNCH_TARGET_TOAST_BODY = "This download has no file the emulator can launch. The files are on disk — see the game page.";
async function romHasLaunchTarget(romId, context) {
    const installed = await getInstalledRom(romId).catch((e) => {
        logError(`${context} launch-target check threw (allowing launch): ${e}`);
        return null;
    });
    return installed == null || installed.launchable;
}

function saveSyncToastBody(uploaded, downloaded) {
    const up = uploaded ?? 0;
    const down = downloaded ?? 0;
    if (up > 0 && down > 0)
        return `Saves synced with RomM (${up} up, ${down} down)`;
    if (up > 0)
        return "Saves uploaded to RomM";
    if (down > 0)
        return "Saves downloaded from RomM";
    return null;
}

function stateTransaction(block) {
    const globals = typeof __mobxGlobals !== "undefined" ? __mobxGlobals : undefined;
    if (!globals)
        return block();
    const prev = globals.allowStateChanges;
    globals.allowStateChanges = true;
    try {
        return block();
    }
    finally {
        globals.allowStateChanges = prev;
    }
}

let metadataCache = {};
let appIdToRomId$1 = {};
let registeredAppIds = new Set();
function getMetadataForAppId(appId) {
    const romId = appIdToRomId$1[appId];
    if (romId == null)
        return null;
    return metadataCache[String(romId)] || null;
}
function applyDirectMutations(appId, metadata) {
    const overview = appStore.GetAppOverviewByAppID(appId);
    if (!overview)
        return false;
    stateTransaction(() => {
        overview.controller_support = 2;
        if (metadata.average_rating != null) {
            overview.metacritic_score = Math.round(metadata.average_rating);
        }
        if (overview.m_setStoreCategories && metadata.steam_categories) {
            for (const cat of metadata.steam_categories) {
                overview.m_setStoreCategories.add(cat);
            }
        }
    });
    return true;
}
function registerMetadataPatches(cache, appIdMap) {
    metadataCache = cache;
    appIdToRomId$1 = {};
    for (const [appIdStr, romId] of Object.entries(appIdMap)) {
        appIdToRomId$1[Number(appIdStr)] = romId;
    }
    registeredAppIds = new Set(Object.keys(appIdToRomId$1).map(Number));
    logInfo(`Registered metadata for ${registeredAppIds.size} apps`);
}
function tryApplyMetadata(appIds, signal) {
    const notApplied = [];
    for (const appId of appIds) {
        if (signal?.aborted)
            break;
        const meta = getMetadataForAppId(appId);
        if (!meta)
            continue;
        if (!applyDirectMutations(appId, meta))
            notApplied.push(appId);
    }
    return notApplied;
}
async function applyAllMetadata(signal) {
    let pending = [...registeredAppIds].filter((appId) => getMetadataForAppId(appId) != null);
    if (pending.length === 0)
        return;
    const delays = [0, 1000, 3000, 5000];
    for (let attempt = 0; attempt < delays.length && pending.length > 0; attempt++) {
        if (delays[attempt] > 0) {
            await new Promise((r) => setTimeout(r, delays[attempt]));
        }
        if (signal?.aborted)
            return;
        pending = tryApplyMetadata(pending, signal);
        if (pending.length > 0 && attempt < delays.length - 1) {
            detach(debugLog(`applyAllMetadata: attempt ${attempt + 1}, ${pending.length} apps not in appStore yet, retrying in ${delays[attempt + 1]}ms...`));
        }
    }
    if (pending.length > 0) {
        detach(debugLog(`applyAllMetadata: ${pending.length} apps still unavailable in appStore after all retries`));
    }
    else {
        detach(debugLog(`applyAllMetadata: all metadata mutations applied`));
    }
}
function unregisterMetadataPatches() {
    metadataCache = {};
    appIdToRomId$1 = {};
    registeredAppIds = new Set();
    logInfo("Cleared metadata state");
}
function updatePlaytimeDisplay(appId, totalSeconds, updateLastPlayed = true) {
    if (!Number.isFinite(totalSeconds) || totalSeconds < 0) {
        detach(debugLog(`updatePlaytimeDisplay: appId=${appId} invalid total=${totalSeconds}, skipping`));
        return false;
    }
    const overview = appStore.GetAppOverviewByAppID(appId);
    if (!overview) {
        detach(debugLog(`updatePlaytimeDisplay: appId=${appId} overview=null, skipping`));
        return false;
    }
    const totalMinutes = Math.floor(totalSeconds / 60);
    if (totalMinutes <= 0)
        return true;
    const prevMinutes = overview.minutes_playtime_forever;
    const prevLastPlayed = overview.rt_last_time_played;
    stateTransaction(() => {
        overview.minutes_playtime_forever = totalMinutes;
        if (updateLastPlayed) {
            overview.rt_last_time_played = Math.floor(Date.now() / 1000);
        }
    });
    detach(debugLog(`updatePlaytimeDisplay: appId=${appId} wrote ${totalMinutes}min (was ${prevMinutes}), rt_last_time_played was ${prevLastPlayed}`));
    globalThis.dispatchEvent(new CustomEvent("romm_playtime_changed", { detail: { appId } }));
    return true;
}
function tryWritePlaytime(items, signal) {
    const notWritten = [];
    for (const item of items) {
        if (signal?.aborted)
            break;
        if (!updatePlaytimeDisplay(item.appId, item.totalSeconds, false)) {
            notWritten.push(item);
        }
    }
    return notWritten;
}
function playtimeItemsToApply(playtimeMap, appIdMap) {
    const romIdToAppId = {};
    for (const [appIdStr, romId] of Object.entries(appIdMap)) {
        romIdToAppId[String(romId)] = Number(appIdStr);
    }
    const pending = [];
    for (const [romIdStr, entry] of Object.entries(playtimeMap)) {
        const appId = romIdToAppId[romIdStr];
        if (appId && entry.total_seconds > 0) {
            pending.push({ appId, totalSeconds: entry.total_seconds });
        }
    }
    return pending;
}
async function applyAllPlaytime(playtimeMap, appIdMap, signal) {
    let pending = playtimeItemsToApply(playtimeMap, appIdMap);
    detach(debugLog(`applyAllPlaytime: ${Object.keys(playtimeMap).length} entries in playtimeMap, ${pending.length} with appId and >0 seconds`));
    if (pending.length === 0)
        return;
    const delays = [0, 1000, 3000, 5000];
    for (let attempt = 0; attempt < delays.length && pending.length > 0; attempt++) {
        if (delays[attempt] > 0) {
            await new Promise((r) => setTimeout(r, delays[attempt]));
        }
        if (signal?.aborted)
            return;
        pending = tryWritePlaytime(pending, signal);
        if (pending.length > 0 && attempt < delays.length - 1) {
            detach(debugLog(`applyAllPlaytime: attempt ${attempt + 1}, ${pending.length} apps not in appStore yet, retrying in ${delays[attempt + 1]}ms...`));
        }
    }
    if (pending.length > 0) {
        detach(debugLog(`applyAllPlaytime: ${pending.length} apps still unavailable in appStore after all retries`));
    }
}

const SOURCE_LABEL = "SteamUIStore.RunningApps";
function coerceRunningApp(value) {
    if (typeof value !== "object" || value === null)
        return null;
    const rec = value;
    const appid = rec.appid;
    if (typeof appid !== "number")
        return null;
    const name = typeof rec.display_name === "string"
        ? rec.display_name
        : typeof rec.strDisplayName === "string"
            ? rec.strDisplayName
            : "";
    return { appid, display_name: name };
}
function coerceRunningAppList(value) {
    if (value === null || value === undefined)
        return [];
    let items;
    if (Array.isArray(value)) {
        items = value;
    }
    else if (typeof value[Symbol.iterator] === "function") {
        items = Array.from(value);
    }
    else {
        return [];
    }
    const apps = [];
    for (const item of items) {
        const app = coerceRunningApp(item);
        if (app)
            apps.push(app);
    }
    return apps;
}
function describeList(apps, raw) {
    if (apps.length > 0)
        return `[${apps.map((a) => a.appid).join(",")}]`;
    if (raw === null || raw === undefined)
        return "absent";
    return "empty";
}
function readRunningApps() {
    if (typeof SteamUIStore === "undefined" || SteamUIStore === null) {
        return { apps: [], diagnostics: `${SOURCE_LABEL}=no-store` };
    }
    try {
        const raw = SteamUIStore.RunningApps;
        const apps = coerceRunningAppList(raw);
        return { apps, diagnostics: `${SOURCE_LABEL}=${describeList(apps, raw)}` };
    }
    catch (e) {
        return { apps: [], diagnostics: `${SOURCE_LABEL}=threw:${e}` };
    }
}
function isAppRunning(appId) {
    return readRunningApps().apps.some((app) => app.appid === appId);
}
function isAnyAppRunning() {
    return readRunningApps().apps.length > 0;
}

const activeSessions = new Map();
let lifecycleChain = Promise.resolve();
let sessionEpoch = 0;
let lifetimeHook = null;
let appIdToRomId = {};
function getRomIdForApp(appId) {
    const romId = appIdToRomId[String(appId)];
    return romId ?? null;
}
function getAppIdRomIdMapSnapshot() {
    return appIdToRomId;
}
function isSessionActive(romId) {
    for (const session of activeSessions.values()) {
        if (session.romId === romId)
            return true;
    }
    return false;
}
async function refreshAppIdMap() {
    try {
        appIdToRomId = await getAppIdRomIdMap();
    }
    catch (e) {
        logError(`Failed to refresh app ID map: ${e}`);
    }
}
const SESSION_BREADCRUMB_KEY = "romm-tender:active-session";
const SESSION_BREADCRUMB_VERSION = 2;
function toSessionEntry(value) {
    if (typeof value !== "object" || value === null)
        return null;
    const { appId, romId, startMs } = value;
    if (typeof appId !== "number" || typeof romId !== "number" || typeof startMs !== "number")
        return null;
    return { appId, romId, startMs };
}
function readSessionBreadcrumbs() {
    try {
        const raw = localStorage.getItem(SESSION_BREADCRUMB_KEY);
        if (raw === null)
            return [];
        const parsed = JSON.parse(raw);
        if (typeof parsed !== "object" || parsed === null)
            return [];
        const crumb = parsed;
        if (crumb.v === 2) {
            if (!Array.isArray(crumb.sessions))
                return [];
            return crumb.sessions.map(toSessionEntry).filter((s) => s !== null);
        }
        if (crumb.v === 1) {
            const lifted = toSessionEntry(crumb);
            return lifted === null ? [] : [lifted];
        }
        return [];
    }
    catch (e) {
        logError(`Failed to read session breadcrumb: ${e}`);
        return [];
    }
}
function persistSessions() {
    if (activeSessions.size === 0) {
        try {
            localStorage.removeItem(SESSION_BREADCRUMB_KEY);
        }
        catch (e) {
            logError(`Failed to clear session breadcrumb: ${e}`);
        }
        return;
    }
    try {
        const row = { v: SESSION_BREADCRUMB_VERSION, sessions: [...activeSessions.values()] };
        localStorage.setItem(SESSION_BREADCRUMB_KEY, JSON.stringify(row));
    }
    catch (e) {
        logError(`Failed to write session breadcrumb: ${e}`);
    }
}
function dispatchSessionChanged(running, appId, romId) {
    globalThis.dispatchEvent(new CustomEvent("romm_session_changed", { detail: { running, appId, romId } }));
}
async function handleGameStart(appId) {
    const open = activeSessions.get(appId);
    if (open) {
        detach(debugLog(`Session start ignored: appId=${appId} already has an open session (romId=${open.romId})`));
        dispatchSessionChanged(true, open.appId, open.romId);
        return;
    }
    const romId = getRomIdForApp(appId);
    if (!romId)
        return;
    logInfo(`Session start: romId=${romId}, appId=${appId}`);
    activeSessions.set(appId, { appId, romId, startMs: Date.now() });
    dispatchSessionChanged(true, appId, romId);
    persistSessions();
    try {
        await recordSessionStart(romId);
    }
    catch (e) {
        logError(`Failed to record session start: ${e}`);
    }
}
async function handleGameStop(stoppedAppId) {
    const session = activeSessions.get(stoppedAppId);
    if (!session) {
        detach(debugLog(`Session stop ignored: appId=${stoppedAppId} opened no session`));
        return;
    }
    const { appId, romId } = session;
    logInfo(`Session end: romId=${romId}`);
    dispatchSessionChanged(false, appId, romId);
    activeSessions.delete(appId);
    persistSessions();
    try {
        const result = await finalizeGameSession(romId);
        if (result.total_seconds != null) {
            updatePlaytimeDisplay(appId, result.total_seconds);
        }
        const directionalBody = result.sync.success
            ? saveSyncToastBody(result.sync.uploaded, result.sync.downloaded)
            : null;
        if (directionalBody) {
            showToast(directionalBody);
        }
        else if (result.sync.failure_toast) {
            showToast(result.sync.failure_toast);
        }
        globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "save_sync", rom_id: romId } }));
        if (result.sync.conflicts_toast) {
            showToast(result.sync.conflicts_toast);
        }
        if (result.migration) {
            setMigrationStatus(result.migration.retrodeck);
            setSaveSortMigrationStatus(result.migration.save_sort);
        }
    }
    catch (e) {
        logError(`Failed to finalize game session: ${e}`);
    }
}
const ADOPTION_POLL_INTERVAL_MS = 500;
const ADOPTION_POLL_MAX_MS = 15000;
async function pollForRunningApps(wanted) {
    const started = Date.now();
    for (;;) {
        const reading = readRunningApps();
        detach(debugLog(`adoption poll round: ${reading.diagnostics}`));
        const surfaced = new Set(reading.apps.map((app) => app.appid));
        if (surfaced.size > 0 && [...wanted].every((appId) => surfaced.has(appId)))
            return reading;
        if (Date.now() - started >= ADOPTION_POLL_MAX_MS)
            return reading;
        await delay(ADOPTION_POLL_INTERVAL_MS);
    }
}
function planAdoption(crumbs, runningAppIds, tracked, resolveRomId, nowMs) {
    const running = new Set(runningAppIds);
    const adopted = [];
    const orphans = [];
    for (const crumb of crumbs) {
        if (tracked.has(crumb.appId))
            continue;
        (running.has(crumb.appId) ? adopted : orphans).push(crumb);
    }
    const attested = new Set(adopted.map((session) => session.appId));
    const restamped = [];
    for (const appId of runningAppIds) {
        if (tracked.has(appId) || attested.has(appId))
            continue;
        const romId = resolveRomId(appId);
        if (romId !== null)
            restamped.push({ appId, romId, startMs: nowMs });
    }
    return { adopted, restamped, orphans };
}
async function adoptOrphanedSessions() {
    const epoch = sessionEpoch;
    const pollStart = Date.now();
    const crumbs = readSessionBreadcrumbs();
    const reading = await pollForRunningApps(new Set(crumbs.map((c) => c.appId)));
    if (epoch !== sessionEpoch) {
        detach(debugLog("adoption: cancelled by destroy"));
        return;
    }
    const waitedMs = Date.now() - pollStart;
    logInfo(reading.apps.length > 0
        ? `adoption: running app appeared after ${waitedMs}ms [${reading.diagnostics}]`
        : `adoption: no running app after ${waitedMs}ms [${reading.diagnostics}]`);
    const { adopted, restamped, orphans } = planAdoption(crumbs, reading.apps.map((app) => app.appid), new Set(activeSessions.keys()), getRomIdForApp, Date.now());
    const recovered = [...adopted, ...restamped];
    for (const session of recovered)
        activeSessions.set(session.appId, session);
    persistSessions();
    for (const session of recovered)
        dispatchSessionChanged(true, session.appId, session.romId);
    for (const s of adopted)
        logInfo(`Adopted running session from breadcrumb: romId=${s.romId}, appId=${s.appId}`);
    for (const s of orphans)
        logInfo(`Session orphaned — playtime not recorded (romId=${s.romId})`);
    for (const session of restamped) {
        if (epoch !== sessionEpoch) {
            detach(debugLog("adoption: cancelled by destroy"));
            return;
        }
        try {
            await recordSessionStart(session.romId);
        }
        catch (e) {
            logError(`Failed to record session start on adoption: ${e}`);
        }
        logInfo(`Adopted running session without breadcrumb, re-stamped marker: romId=${session.romId}, appId=${session.appId}`);
    }
}
async function initSessionManager() {
    await refreshAppIdMap();
    lifetimeHook = SteamClient.GameSessions.RegisterForAppLifetimeNotifications((update) => {
        lifecycleChain = lifecycleChain
            .then(async () => {
            if (update.bRunning) {
                const appId = update.unAppID;
                if (appId) {
                    await refreshAppIdMap();
                    await handleGameStart(appId);
                }
            }
            else {
                await handleGameStop(update.unAppID);
            }
        })
            .catch((e) => {
            logError(`Lifecycle event error: ${e}`);
        });
    });
    const adoption = lifecycleChain
        .then(() => adoptOrphanedSessions())
        .catch((e) => {
        logError(`Session adoption error: ${e}`);
    });
    lifecycleChain = adoption;
    await adoption;
    logInfo("Session manager initialized");
}
function destroySessionManager() {
    if (lifetimeHook) {
        lifetimeHook.unregister();
        lifetimeHook = null;
    }
    activeSessions.clear();
    lifecycleChain = Promise.resolve();
    sessionEpoch++;
    logInfo("Session manager destroyed");
}

const SAVEFILES_IN_CONTENT_DIR_REASON = "savefiles_in_content_dir";
const SAVE_SHAPE_UNSUPPORTED_REASON = "save_shape_unsupported";
const BENIGN_SYNC_SKIP_REASONS = [
    SAVEFILES_IN_CONTENT_DIR_REASON,
    SAVE_SHAPE_UNSUPPORTED_REASON,
];

const SETTINGS_SECTIONS = [
    "connections",
    "save-sync",
    "controller",
    "steam-library",
    "cores",
    "advanced",
];

class TimeoutError extends Error {
    constructor(ms) {
        super(`callable timed out after ${ms}ms`);
        this.name = "TimeoutError";
    }
}
function withTimeout(promise, ms) {
    let timer;
    const timeout = new Promise((_, reject) => {
        timer = setTimeout(() => reject(new TimeoutError(ms)), ms);
    });
    return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

const RELEASE_TIMEOUT_MS = 5000;
const RENEW_INTERVAL_MS = 60000;
const CONTINUATION_TIMEOUT_MS = 5 * 60000;
const activeLeases = new Map();
const ownerGenerations = new Map();
let pluginGeneration = 0;
let pluginMounted = true;
class UnsettledContinuation {
    constructor(error) {
        this.error = error;
    }
}
class PruneLeaseAdmissionCancelled extends Error {
}
function isPruneLeaseCancelled(signal) {
    return signal?.aborted ?? false;
}
function isPruneLeaseCancellation(error, admission) {
    return error instanceof PruneLeaseAdmissionCancelled || !isPruneLeaseAdmissionCurrent(admission);
}
function mountPruneLeasePlugin() {
    pluginGeneration++;
    pluginMounted = true;
    void releaseOrphanedPruneLeases()
        .then((result) => {
        if (result.released > 0) {
            logError(`prune lease: disowned ${result.released} lease(s) stranded by a previous frontend context`);
        }
    })
        .catch((e) => logError(`prune lease: could not disown stranded leases: ${e}`));
}
function mountPruneLeaseOwner(owner) {
    const current = ownerGenerations.get(owner);
    if (current?.mounted)
        return;
    ownerGenerations.set(owner, { generation: (current?.generation ?? 0) + 1, mounted: true });
}
function capturePruneLeaseAdmission(owner) {
    const current = owner === undefined ? undefined : ownerGenerations.get(owner);
    return {
        pluginGeneration,
        ...(owner === undefined ? {} : { owner, ownerGeneration: current?.generation ?? 0 }),
    };
}
function isPruneLeaseAdmissionCurrent(admission) {
    if (!pluginMounted || admission.pluginGeneration !== pluginGeneration)
        return false;
    if (admission.owner === undefined)
        return true;
    const current = ownerGenerations.get(admission.owner);
    return current?.mounted === true && current.generation === admission.ownerGeneration;
}
async function releasePruneLease(token, context) {
    try {
        await withTimeout(releasePruneConflictLease(token), RELEASE_TIMEOUT_MS);
    }
    catch (e) {
        logError(`${context}: failed to release prune lease: ${e}`);
    }
}
async function finishLease(token, releaseBackend) {
    const active = activeLeases.get(token);
    if (!active)
        return;
    activeLeases.delete(token);
    clearInterval(active.interval);
    if (releaseBackend)
        await releasePruneLease(token, active.context);
}
function retireLeaseAfterSettlement(token) {
    const active = activeLeases.get(token);
    if (!active)
        return Promise.resolve();
    activeLeases.delete(token);
    clearInterval(active.interval);
    active.abortController?.abort();
    const release = () => releasePruneLease(token, active.context);
    return active.settlement ? active.settlement.then(release) : release();
}
function maintainPruneLease(token, context, owner = context, abortController, settlement) {
    const renew = async () => {
        if (!activeLeases.has(token))
            return;
        try {
            const result = await withTimeout(renewPruneConflictLease(token), RELEASE_TIMEOUT_MS);
            if (!result.success) {
                logError(`${context}: prune lease renewal was refused: ${result.message}`);
                activeLeases.get(token)?.abortController?.abort();
                await finishLease(token, false);
            }
        }
        catch (e) {
            logError(`${context}: failed to renew prune lease: ${e}`);
        }
    };
    const interval = setInterval(() => void renew(), RENEW_INTERVAL_MS);
    activeLeases.set(token, { abortController, context, owner, interval, settlement });
    return () => finishLease(token, true);
}
async function releasePruneLeasesByOwner(owner) {
    const current = ownerGenerations.get(owner);
    ownerGenerations.set(owner, { generation: (current?.generation ?? 0) + 1, mounted: false });
    const owned = [...activeLeases].filter(([, lease]) => lease.owner === owner);
    for (const [, lease] of owned)
        lease.abortController?.abort();
    const tokens = owned.map(([token]) => token);
    await Promise.all(tokens.map(retireLeaseAfterSettlement));
}
async function releaseAllPruneLeases() {
    pluginGeneration++;
    pluginMounted = false;
    for (const [owner, current] of ownerGenerations) {
        ownerGenerations.set(owner, { generation: current.generation + 1, mounted: false });
    }
    for (const lease of activeLeases.values())
        lease.abortController?.abort();
    await Promise.all([...activeLeases].map(([token]) => retireLeaseAfterSettlement(token)));
}
async function boundedContinuation(promise) {
    const settled = promise.then((result) => ({ kind: "result", result }), (error) => ({ kind: "error", error }));
    let timer;
    const timeout = new Promise((resolve) => {
        timer = setTimeout(() => resolve({ kind: "timeout", error: new Error(`callable timed out after ${CONTINUATION_TIMEOUT_MS}ms`) }), CONTINUATION_TIMEOUT_MS);
    });
    try {
        const outcome = await Promise.race([settled, timeout]);
        if (outcome.kind === "timeout")
            throw new UnsettledContinuation(outcome.error);
        if (outcome.kind === "error")
            throw outcome.error;
        return { result: outcome.result, settled: true };
    }
    finally {
        clearTimeout(timer);
    }
}
async function withPruneLeases(tokens, context, operation, owner = context, admission = capturePruneLeaseAdmission()) {
    const uniqueTokens = [...new Set(tokens.filter((token) => !!token))];
    if (!isPruneLeaseAdmissionCurrent(admission)) {
        await Promise.all(uniqueTokens.map((token) => releasePruneLease(token, context)));
        throw new PruneLeaseAdmissionCancelled(`${context}: continuation was cancelled before lease registration`);
    }
    const abortController = new AbortController();
    const operationPromise = Promise.resolve().then(() => operation(abortController.signal));
    const settlement = operationPromise.then(() => undefined, () => undefined);
    const releases = uniqueTokens.map((token) => ({
        token,
        release: maintainPruneLease(token, context, owner, abortController, settlement),
    }));
    let timedOut = false;
    try {
        return (await boundedContinuation(operationPromise)).result;
    }
    catch (error_) {
        if (error_ instanceof UnsettledContinuation) {
            timedOut = true;
            abortController.abort();
            for (const { token } of releases)
                void retireLeaseAfterSettlement(token);
            throw error_.error;
        }
        throw error_;
    }
    finally {
        if (!timedOut)
            await Promise.all(releases.map(({ release }) => release()));
    }
}
function withPruneLease(token, context, operation, owner = context, admission) {
    return withPruneLeases([token], context, operation, owner, admission);
}

const CONCURRENCY = 10;
const RECONFIRM_FETCH_TIMEOUT_MS = 3000;
function releaseLateReconfirmLease(fetchOutcome, context) {
    void fetchOutcome
        .then(async (late) => {
        if (late.kind === "result" && late.item?.success) {
            await releasePruneLease(late.item.prune_lease_token, `${context}: timed-out launch_options re-confirm`);
        }
    })
        .catch((error) => logError(`${context}: late launch_options re-confirm cleanup failed: ${error}`));
}
async function fetchRelaunchOptions(romId, context, admission) {
    const fetchOutcome = getRomRelaunchOptions(romId).then((item) => ({ kind: "result", item }), (error) => ({ kind: "error", error }));
    let timer;
    const timeout = new Promise((resolve) => {
        timer = setTimeout(() => resolve({ kind: "timeout" }), RECONFIRM_FETCH_TIMEOUT_MS);
    });
    const outcome = await Promise.race([fetchOutcome, timeout]);
    if (outcome.kind === "timeout") {
        logError(`${context}: launch_options re-confirm timed out (launch cancelled)`);
        releaseLateReconfirmLease(fetchOutcome, context);
        const status = isPruneLeaseAdmissionCurrent(admission) ? "timeout" : "cancelled";
        return { kind: "verdict", result: { status } };
    }
    clearTimeout(timer);
    if (outcome.kind === "error") {
        if (!isPruneLeaseAdmissionCurrent(admission))
            return { kind: "verdict", result: { status: "cancelled" } };
        logError(`${context}: launch_options re-confirm failed (launching anyway): ${outcome.error}`);
        return { kind: "verdict", result: { status: "best_effort_failure" } };
    }
    const item = outcome.item;
    if (!item) {
        const status = isPruneLeaseAdmissionCurrent(admission) ? "ready" : "cancelled";
        return { kind: "verdict", result: { status } };
    }
    if (!item.success) {
        if (!isPruneLeaseAdmissionCurrent(admission))
            return { kind: "verdict", result: { status: "cancelled" } };
        logError(`${context}: launch_options re-confirm failed (launching anyway): ${item.message}`);
        return { kind: "verdict", result: { status: "best_effort_failure" } };
    }
    return { kind: "options", options: item };
}
async function reconfirmLaunchOptions(romId, appId, context, admission = capturePruneLeaseAdmission()) {
    if (!isPruneLeaseAdmissionCurrent(admission))
        return { status: "cancelled" };
    const fetched = await fetchRelaunchOptions(romId, context, admission);
    if (fetched.kind === "verdict")
        return fetched.result;
    const item = fetched.options;
    try {
        await withPruneLease(item.prune_lease_token, context, async (signal) => {
            if (signal.aborted)
                return;
            await setLaunchOptionsConfirmed(appId, item.launch_options);
        }, context, admission);
        return { status: isPruneLeaseAdmissionCurrent(admission) ? "ready" : "cancelled" };
    }
    catch (e) {
        if (isPruneLeaseCancellation(e, admission)) {
            return { status: "cancelled" };
        }
        logError(`${context}: launch_options re-confirm failed (launching anyway): ${e}`);
        return { status: "best_effort_failure" };
    }
}
async function batchConfirmLaunchOptions(items, context, signal) {
    if (!Array.isArray(items) || items.length === 0)
        return;
    for (let i = 0; i < items.length; i += CONCURRENCY) {
        const batch = items.slice(i, i + CONCURRENCY);
        await Promise.all(batch.map(async (item) => {
            if (signal?.aborted)
                return;
            try {
                const ok = await setLaunchOptionsConfirmed(item.app_id, item.launch_options);
                if (!ok) {
                    logError(`${context}: failed to confirm launch options for appId ${item.app_id}`);
                }
            }
            catch (e) {
                logError(`${context}: failed to set launch options for appId ${item.app_id}: ${e}`);
            }
        }));
    }
}

function lerpColor(a, b, t) {
    const r = Math.round(a[0] + (b[0] - a[0]) * t);
    const g = Math.round(a[1] + (b[1] - a[1]) * t);
    const bl = Math.round(a[2] + (b[2] - a[2]) * t);
    return `rgb(${r}, ${g}, ${bl})`;
}
const BLUE_LEFT = [26, 159, 255];
const BLUE_RIGHT = [0, 120, 212];
const GREEN_LEFT = [80, 200, 47];
const GREEN_RIGHT = [24, 177, 78];
function formatProgress(downloaded, total) {
    if (total < 1024)
        return `${downloaded} / ${total} B`;
    if (total < 1024 * 1024)
        return `${(downloaded / 1024).toFixed(1)} / ${(total / 1024).toFixed(1)} KB`;
    if (total < 1024 * 1024 * 1024)
        return `${(downloaded / (1024 * 1024)).toFixed(1)} / ${(total / (1024 * 1024)).toFixed(1)} MB`;
    return `${(downloaded / (1024 * 1024 * 1024)).toFixed(2)} / ${(total / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}
const CustomPlayButton = ({ appId }) => {
    const leaseOwner = `custom-play-button:${appId}`;
    const [state, setState] = SP_REACT.useState("loading");
    const [romId, setRomId] = SP_REACT.useState(null);
    const [romName, setRomName] = SP_REACT.useState("");
    const [actionPending, setActionPending] = SP_REACT.useState(false);
    const [dlProgress, setDlProgress] = SP_REACT.useState(null);
    const [isOffline, setIsOffline] = SP_REACT.useState(getRommConnectionState() === "offline");
    const [boundVanished, setBoundVanished] = SP_REACT.useState(() => isBoundVanished(appId));
    const [isRunning, setIsRunning] = SP_REACT.useState(false);
    const [stopPending, setStopPending] = SP_REACT.useState(false);
    const [targetOccupied, setTargetOccupied] = SP_REACT.useState(false);
    const [candidatePresent, setCandidatePresent] = SP_REACT.useState(false);
    const [uninstallProgress, setUninstallProgress] = SP_REACT.useState(null);
    const uninstallPendingRef = SP_REACT.useRef(false);
    const romIdRef = SP_REACT.useRef(null);
    const containerRef = SP_REACT.useRef(null);
    const transitionTimerRef = SP_REACT.useRef(null);
    const enterDownloadState = (occupied = false, candidate = false) => {
        setTargetOccupied(occupied);
        setCandidatePresent(candidate);
        setState("download");
    };
    SP_REACT.useEffect(() => {
        mountPruneLeaseOwner(leaseOwner);
        return () => {
            detach(releasePruneLeasesByOwner(leaseOwner));
        };
    }, [leaseOwner]);
    SP_REACT.useEffect(() => {
        const cls = basicAppDetailsSectionStylerClasses?.PlaySection;
        if (cls)
            hideNativePlaySection(cls);
        return () => {
            showNativePlaySection();
        };
    }, []);
    SP_REACT.useEffect(() => {
        return () => {
            if (transitionTimerRef.current)
                clearTimeout(transitionTimerRef.current);
        };
    }, []);
    const rehydrateInflightDownload = async (rid) => {
        try {
            const queue = await getDownloadQueue();
            const entry = queue.downloads.find((d) => d.rom_id === rid);
            if (entry &&
                (entry.status === "downloading" ||
                    entry.status === "queued" ||
                    entry.status === "paused" ||
                    entry.status === "extracting")) {
                setActionPending(true);
                setDlProgress({
                    bytesDownloaded: entry.bytes_downloaded,
                    totalBytes: entry.total_bytes,
                    resumable: entry.status === "extracting" ? false : entry.resumable,
                    paused: entry.status === "paused",
                    extracting: entry.status === "extracting",
                });
            }
        }
        catch (e) {
            logError(`CustomPlayButton: failed to rehydrate download state: ${e}`);
        }
    };
    SP_REACT.useEffect(() => {
        let cancelled = false;
        async function init() {
            try {
                const cached = await getCachedGameDetail(appId);
                detach(debugLog(`CustomPlayButton init: appId=${appId} cached.found=${cached.found} cancelled=${cancelled}`));
                if (cancelled)
                    return;
                if (!cached.found) {
                    detach(debugLog(`CustomPlayButton: -> not_romm (not in cache)`));
                    setState("not_romm");
                    return;
                }
                const rid = cached.rom_id;
                setRomId(rid);
                romIdRef.current = rid;
                if (cached.rom_name)
                    setRomName(cached.rom_name);
                setIsRunning(isSessionActive(rid) || isAppRunning(appId));
                if (cached.installed) {
                    const hasConflict = hasAnySaveConflict(cached.save_status);
                    if (hasConflict) {
                        detach(debugLog(`CustomPlayButton: -> conflict (from cache)`));
                        setState("conflict");
                    }
                    else {
                        detach(debugLog(`CustomPlayButton: -> play`));
                        setState("play");
                    }
                }
                else {
                    detach(debugLog(`CustomPlayButton: -> download`));
                    enterDownloadState(cached.target_path_occupied === true, cached.adoption_candidate_present === true);
                    await rehydrateInflightDownload(rid);
                }
            }
            catch (e) {
                logError(`CustomPlayButton init error: ${e}`);
                if (!cancelled) {
                    setState("not_romm");
                }
            }
        }
        detach(init());
        return () => {
            cancelled = true;
        };
    }, [appId]);
    SP_REACT.useEffect(() => {
        let lastAnnouncedState = null;
        const progressListener = addEventListener("download_progress", (evt) => {
            if (evt.rom_id !== romIdRef.current)
                return;
            if (evt.status === "failed" || evt.status === "cancelled") {
                enterDownloadState();
                setActionPending(false);
                setDlProgress(null);
            }
            else {
                const extracting = evt.status === "extracting";
                setDlProgress((prev) => ({
                    bytesDownloaded: evt.bytes_downloaded,
                    totalBytes: evt.total_bytes,
                    resumable: extracting ? false : (evt.resumable ?? prev?.resumable ?? false),
                    paused: extracting ? false : evt.status === "paused",
                    extracting,
                }));
            }
        });
        const completeListener = addEventListener("download_complete", (evt) => {
            if (evt.rom_id !== romIdRef.current)
                return;
            setDlProgress(null);
            setActionPending(false);
            lastAnnouncedState = null;
            setState("dl_complete");
            transitionTimerRef.current = setTimeout(() => {
                const announced = lastAnnouncedState;
                lastAnnouncedState = null;
                setState(announced !== null && announced.romId === romIdRef.current ? announced.state : "play");
            }, 1100);
        });
        const failedListener = addEventListener("download_failed", (evt) => handleButtonDownloadFailure(evt, romIdRef.current, () => {
            setDlProgress(null);
            setActionPending(false);
            enterDownloadState();
        }));
        const uninstallProgressListener = addEventListener("uninstall_progress", (evt) => {
            if (evt.rom_id !== romIdRef.current)
                return;
            setUninstallProgress({ removed: evt.files_removed, total: evt.files_total });
        });
        const onUninstall = (e) => {
            const romId = e.detail?.rom_id;
            if (romId !== romIdRef.current)
                return;
            setState((prev) => (prev === "uninstalling" ? prev : "download"));
            setActionPending(false);
            setTargetOccupied(false);
            setCandidatePresent(false);
        };
        globalThis.addEventListener("romm_rom_uninstalled", onUninstall);
        const handleVersionSwitched = async () => {
            const cached = await getCachedGameDetail(appId);
            if (!cached.found || cached.rom_id == null) {
                logError(`CustomPlayButton: version_switched for appId ${appId} but cached detail not found — button may be stale`);
                return;
            }
            const rid = cached.rom_id;
            setRomId(rid);
            romIdRef.current = rid;
            if (cached.rom_name)
                setRomName(cached.rom_name);
            if (cached.installed) {
                setState(hasAnySaveConflict(cached.save_status) ? "conflict" : "play");
            }
            else {
                setDlProgress(null);
                setActionPending(false);
                enterDownloadState(cached.target_path_occupied === true, cached.adoption_candidate_present === true);
            }
        };
        const onDataChanged = (e) => {
            const detail = e.detail;
            if (detail?.type === "version_switched") {
                if (detail.app_id !== appId)
                    return;
                detach(handleVersionSwitched().catch((err) => logError(`CustomPlayButton: version_switched handler failed for appId ${appId}: ${err}`)));
                return;
            }
            if (detail?.type !== "save_sync")
                return;
            if (detail.rom_id && detail.rom_id !== romIdRef.current)
                return;
            if (detail.has_conflict === undefined)
                return;
            const announced = detail.has_conflict ? "conflict" : "play";
            lastAnnouncedState = { romId: romIdRef.current, state: announced };
            setState((prev) => {
                if (prev === "uninstall_pending" || prev === "uninstalling")
                    return prev;
                if (prev === "dl_complete")
                    return prev;
                if (prev === "syncing" || prev === "launching" || prev === "download")
                    return prev;
                return announced;
            });
        };
        globalThis.addEventListener("romm_data_changed", onDataChanged);
        const unsubscribeConnection = onRommConnectionChange((s) => setIsOffline(s === "offline"));
        const unsubscribeVanished = onBoundVanishedChange(() => setBoundVanished(isBoundVanished(appId)));
        const onSessionChanged = (e) => {
            if (e.detail.romId !== romIdRef.current)
                return;
            setIsRunning(e.detail.running);
            if (!e.detail.running) {
                setState((prev) => (prev === "launching" ? "play" : prev));
            }
        };
        globalThis.addEventListener("romm_session_changed", onSessionChanged);
        return () => {
            removeEventListener("download_progress", progressListener);
            removeEventListener("download_complete", completeListener);
            removeEventListener("download_failed", failedListener);
            removeEventListener("uninstall_progress", uninstallProgressListener);
            globalThis.removeEventListener("romm_rom_uninstalled", onUninstall);
            globalThis.removeEventListener("romm_data_changed", onDataChanged);
            unsubscribeConnection();
            unsubscribeVanished();
            globalThis.removeEventListener("romm_session_changed", onSessionChanged);
        };
    }, [appId]);
    SP_REACT.useEffect(() => {
        if (state !== "play" && state !== "download" && state !== "conflict")
            return;
        const timer = setTimeout(() => {
            if (containerRef.current) {
                const btn = containerRef.current.querySelector("button");
                if (btn) {
                    btn.focus();
                    btn.classList.add("gpfocus");
                }
            }
        }, 400);
        return () => clearTimeout(timer);
    }, [state]);
    const ensureTrackingConfigured = async (rid) => {
        const trackingResult = await isSaveTrackingConfigured(rid).catch(() => ({ configured: true }));
        if (trackingResult.configured)
            return "proceed";
        let setupInfo;
        try {
            setupInfo = await getSaveSetupInfo(rid);
        }
        catch {
            return "proceed";
        }
        return applyLaunchGateSetupOutcome(resolveSaveSetupOutcome(setupInfo), {
            rid,
            confirmSlotChoice,
            toast: (body) => showToast(body),
            dispatchSavesTab: () => globalThis.dispatchEvent(new CustomEvent("romm_tab_switch", { detail: { tab: "saves" } })),
        });
    };
    const confirmCoreChangeIfNeeded = async (rid) => {
        const coreCheck = await checkCoreChange(rid).catch(() => ({
            changed: false,
        }));
        if (!coreCheck.changed)
            return true;
        return showCoreChangeModal(coreCheck.old_label ?? coreCheck.old_core ?? "Unknown", coreCheck.new_label ?? coreCheck.new_core ?? "Unknown");
    };
    const runPreLaunchSync = async (rid) => {
        setState("syncing");
        let result;
        try {
            result = await Promise.race([
                preLaunchSync(rid),
                new Promise((_, reject) => setTimeout(() => reject(new Error("timeout")), 15000)),
            ]);
        }
        catch (e) {
            detach(debugLog(`CustomPlayButton: pre-launch sync failed: ${e}`));
            return { success: false, message: "" };
        }
        detach(debugLog(`CustomPlayButton: preLaunchSync result: synced=${result.synced} conflicts=${result.conflicts?.length ?? 0} success=${result.success}`));
        if (result.reason !== undefined && BENIGN_SYNC_SKIP_REASONS.includes(result.reason)) {
            detach(debugLog(`CustomPlayButton: pre-launch sync skipped (${result.reason}) — launching`));
            return { success: true, message: result.message };
        }
        if (result.conflicts && result.conflicts.length > 0) {
            return { success: result.success, message: result.message, conflicts: result.conflicts };
        }
        if (!result.success) {
            detach(debugLog(`CustomPlayButton: pre-launch sync failed: reason=${result.reason ?? ""} errors=[${result.errors?.join(", ") ?? ""}] message=${result.message}`));
            return { success: false, message: result.message };
        }
        const toastBody = saveSyncToastBody(result.uploaded, result.downloaded);
        if (toastBody) {
            showToast(toastBody);
        }
        return { success: true, message: result.message };
    };
    const dispatchLaunch = async (gameId, admission) => {
        if (!isPruneLeaseAdmissionCurrent(admission))
            return;
        setState("launching");
        if (romId) {
            const reconfirm = await reconfirmLaunchOptions(romId, appId, "CustomPlayButton", admission);
            if (reconfirm.status === "cancelled")
                return;
            if (reconfirm.status === "timeout") {
                setState("play");
                return;
            }
        }
        markLaunchSkipped(appId);
        SteamClient.Apps.RunGame(gameId, "", -1, 100);
    };
    const makePlayButtonOps = (rid) => ({
        migrationPending: () => getMigrationState().pending,
        hasLaunchTarget: () => romHasLaunchTarget(rid, "CustomPlayButton"),
        ensureTrackingConfigured: () => ensureTrackingConfigured(rid),
        checkCoreChange: () => confirmCoreChangeIfNeeded(rid),
        checkReachability: async () => {
            try {
                const { online } = await probeReachability();
                reportServerReachable(online);
                return online;
            }
            catch (e) {
                logError(`CustomPlayButton: reachability probe failed (treating as offline): ${e}`);
                return false;
            }
        },
        preLaunchSync: () => runPreLaunchSync(rid),
        checkLocalDrift: async () => (await checkLocalDrift(rid).catch((e) => {
            logError(`CustomPlayButton: local-drift check failed (treating as not-drifted): ${e}`);
            return { drifted: false, rom_id: rid };
        })).drifted,
    });
    const handlePlay = async () => {
        if (state === "syncing" || state === "launching")
            return;
        const overview = appStore.GetAppOverviewByAppID(appId);
        const gameId = overview?.GetGameID?.() ?? String(appId);
        const admission = capturePruneLeaseAdmission(leaseOwner);
        detach(debugLog(`CustomPlayButton: handlePlay appId=${appId} gameId=${gameId}`));
        if (!romId) {
            await dispatchLaunch(gameId, admission);
            return;
        }
        if (isSessionActive(romId) || isAppRunning(appId)) {
            detach(debugLog(`CustomPlayButton: appId=${appId} already running — skipping pre-launch sync`));
            await dispatchLaunch(gameId, admission);
            return;
        }
        try {
            let verdict = await runLaunchGate(appId, romId, makePlayButtonOps(romId));
            while ((await actOnVerdict(verdict, gameId, romId, admission)) === "retry") {
                verdict = await runLaunchGate(appId, romId, makePlayButtonOps(romId));
            }
        }
        catch (e) {
            detach(debugLog(`CustomPlayButton: handlePlay unexpected error — resetting to play: ${e}`));
            setState("play");
        }
    };
    const actOnVerdict = async (verdict, gameId, rid, admission) => {
        switch (verdict.decision) {
            case "allow":
                await dispatchLaunch(gameId, admission);
                return "done";
            case "abort":
            case "block":
                if (verdict.decision === "block" && verdict.reason === "no_launch_target") {
                    showToast(NO_LAUNCH_TARGET_TOAST_BODY);
                }
                setState("play");
                return "done";
            case "conflict": {
                const resolution = await handleConflicts(verdict.conflicts);
                if (resolution === "cancel") {
                    setState("conflict");
                    return "done";
                }
                globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "save_sync", rom_id: rid } }));
                await dispatchLaunch(gameId, admission);
                return "done";
            }
            case "offline_drift": {
                const choice = await showOfflineDriftModal();
                if (choice === "start_anyway") {
                    await dispatchLaunch(gameId, admission);
                    return "done";
                }
                if (choice === "retry") {
                    setState("syncing");
                    return "retry";
                }
                setState("play");
                return "done";
            }
            case "sync_failed": {
                const proceed = await showFallbackLaunchModal(verdict.message);
                if (proceed) {
                    await dispatchLaunch(gameId, admission);
                    return "done";
                }
                setState("play");
                return "done";
            }
        }
    };
    const handleResumeGame = async () => {
        if (!(isAppRunning(appId) || (romId !== null && isSessionActive(romId)))) {
            detach(debugLog(`CustomPlayButton: Resume on appId=${appId} but nothing is running — self-healing to launch`));
            setIsRunning(false);
            await handlePlay();
            return;
        }
        if (typeof SteamUIStore !== "undefined" && SteamUIStore) {
            try {
                SteamUIStore.SetRunningApp(appId);
                if (typeof SteamUIStore.NavigateToRunningApp === "function") {
                    SteamUIStore.NavigateToRunningApp();
                    detach(debugLog(`CustomPlayButton: resumed appId=${appId} via SteamUIStore.NavigateToRunningApp`));
                    return;
                }
            }
            catch (e) {
                detach(debugLog(`CustomPlayButton: resume — SteamUIStore threw, falling back to Navigate: ${e}`));
            }
        }
        DFL.Navigation.Navigate("/apprunning");
        detach(debugLog(`CustomPlayButton: resumed appId=${appId} via Navigation.Navigate`));
    };
    const clearRunningOverlay = () => {
        setIsRunning(false);
        setState((prev) => (prev === "launching" ? "play" : prev));
    };
    const stopInFlightRef = SP_REACT.useRef(false);
    const handleStopGame = async () => {
        if (stopInFlightRef.current) {
            detach(debugLog(`CustomPlayButton: Stop ignored for appId=${appId} — a stop is already in flight`));
            return;
        }
        if (!(isAppRunning(appId) || (romId !== null && isSessionActive(romId)))) {
            detach(debugLog(`CustomPlayButton: Stop on appId=${appId} but nothing is running — clearing stale overlay`));
            clearRunningOverlay();
            return;
        }
        if (romId == null) {
            detach(debugLog(`CustomPlayButton: Stop on appId=${appId} but the rom id is not resolved yet — not stopping`));
            showToast("Couldn't stop the game — still loading its details");
            return;
        }
        if (!(await showStopGameModal())) {
            detach(debugLog(`CustomPlayButton: Stop cancelled for appId=${appId}`));
            return;
        }
        stopInFlightRef.current = true;
        setStopPending(true);
        try {
            const result = await stopRunningGame(romId);
            if (result.success || result.reason === "not_running") {
                detach(debugLog(`CustomPlayButton: stop_running_game for appId=${appId} — success=${result.success} ` +
                    `reason=${result.reason ?? "none"} stopped=${result.stopped ?? 0} forced=${result.force_killed ?? 0}`));
                clearRunningOverlay();
                return;
            }
            detach(debugLog(`CustomPlayButton: stop_running_game refused for appId=${appId} — reason=${result.reason ?? "none"}`));
            showToast(result.message || "Couldn't stop the game");
        }
        catch (e) {
            detach(debugLog(`CustomPlayButton: stop_running_game threw for appId=${appId}: ${e}`));
            showToast("Couldn't stop the game");
        }
        finally {
            stopInFlightRef.current = false;
            setStopPending(false);
        }
    };
    const showRunningActionsMenu = (e) => {
        DFL.showContextMenu(SP_JSX.jsx(DFL.Menu, { label: "Game Actions", children: SP_JSX.jsx(DFL.MenuItem, { tone: "destructive", disabled: stopPending, onClick: () => detach(handleStopGame()), children: stopPending ? "Stopping..." : "Stop Game" }, "stop") }), getEventTarget(e));
    };
    const handleResolveConflict = async () => {
        if (!romId)
            return;
        setState("syncing");
        try {
            const result = await Promise.race([
                getSaveStatus(romId),
                new Promise((_, reject) => setTimeout(() => reject(new Error("timeout")), 15000)),
            ]);
            if (isCallableFailure(result)) {
                detach(debugLog(`CustomPlayButton: resolve conflict deferred: ${result.message}`));
                showToast(result.message);
                setState("conflict");
                return;
            }
            if (result.server_query_failed) {
                const unreachable = result.server_query_reason === "server_unreachable";
                if (unreachable) {
                    reportServerReachable(false);
                }
                detach(debugLog(`CustomPlayButton: resolve conflict — server query failed for rom ${romId}`));
                showToast(unreachable
                    ? "Couldn't reach server to resolve conflict"
                    : "RomM couldn't find this game's save data — conflict left unresolved");
                setState("conflict");
                return;
            }
            reportServerReachable(true);
            if (result.conflicts && result.conflicts.length > 0) {
                const conflictResult = await handleConflicts(result.conflicts);
                if (conflictResult === "cancel") {
                    setState("conflict");
                    return;
                }
            }
            globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "save_sync", rom_id: romId } }));
            setState("play");
        }
        catch (e) {
            detach(debugLog(`CustomPlayButton: resolve conflict failed: ${e}`));
            showToast("Couldn't reach server to resolve conflict");
            setState("conflict");
        }
    };
    const handleDownload = async (replaceExisting = false, discardPath, collisionChoice = null) => {
        if (!romId || actionPending)
            return;
        setActionPending(true);
        try {
            const result = await startDownload(romId, replaceExisting, discardPath ?? null, collisionChoice, !replaceExisting && candidatePresent);
            if (isRenameCollisions(result)) {
                setActionPending(false);
                const answer = await showAdoptCollisionModal(result.collisions);
                if (answer !== "cancel")
                    await handleDownload(replaceExisting, discardPath, answer);
                return;
            }
            if (isTargetOccupied(result)) {
                setTargetOccupied(true);
                setActionPending(false);
                await resolveOccupiedTarget(romId, result);
                return;
            }
            if (isCandidatesFound(result)) {
                setCandidatePresent(true);
                setActionPending(false);
                await resolveCandidates(romId, result);
                return;
            }
            if (isUnusableNamesake(result)) {
                setActionPending(false);
                await resolveUnusable(result);
                return;
            }
            if (isCandidateVanished(result)) {
                setCandidatePresent(false);
                setActionPending(false);
                await resolveVanished(result);
                return;
            }
            if (!result.success) {
                showToast(result.message || "Download failed");
                setActionPending(false);
            }
        }
        catch {
            showToast("Download failed — is RomM server running?");
            setActionPending(false);
        }
    };
    const resolveOccupiedTarget = async (rid, occupied) => {
        const choice = await showAdoptExistingModal(rid, occupied);
        if (choice === "replace") {
            await handleDownload(true);
            return;
        }
        if (choice === "adopt") {
            await handleAdopt(rid);
        }
    };
    const resolveCandidates = async (rid, found) => {
        let candidate = found.candidates[0];
        if (candidate === undefined)
            return;
        if (found.candidates.length > 1) {
            const picked = await showAdoptCandidateModal(found);
            if (picked.kind === "cancel")
                return;
            if (picked.kind === "download") {
                await handleDownload(true);
                return;
            }
            candidate = picked.candidate;
        }
        const choice = await showAdoptExistingModal(rid, comparisonForCandidate(candidate, found.incoming), candidate.path);
        if (choice === "replace") {
            await handleDownload(true, candidate.path);
            return;
        }
        if (choice === "adopt") {
            await handleAdopt(rid, candidate.path);
        }
    };
    const resolveUnusable = async (unusable) => {
        if ((await showAdoptUnusableModal(unusable)) === "download")
            await handleDownload(true);
    };
    const resolveVanished = async (vanished) => {
        if ((await showAdoptVanishedModal(vanished)) === "download")
            await handleDownload(true);
    };
    const handleAdopt = async (rid, candidatePath, collisionChoice = null) => {
        setActionPending(true);
        const admission = capturePruneLeaseAdmission(leaseOwner);
        try {
            const result = await adoptExistingRom(rid, candidatePath ?? null, collisionChoice);
            if (isRenameCollisions(result)) {
                const answer = await showAdoptCollisionModal(result.collisions);
                if (answer !== "cancel")
                    await handleAdopt(rid, candidatePath, answer);
                return;
            }
            if (!result.success) {
                showToast(result.message || "Couldn't use the existing files");
                return;
            }
            const adoptedAppId = result.app_id;
            if (adoptedAppId != null && result.launch_options !== undefined) {
                const launchOptions = result.launch_options;
                await withPruneLease(result.prune_lease_token, "ROM adopt", async (signal) => {
                    if (signal.aborted)
                        return;
                    await setLaunchOptionsConfirmed(adoptedAppId, launchOptions).catch(() => false);
                }, leaseOwner, admission);
            }
            setTargetOccupied(false);
            setCandidatePresent(false);
            setState("play");
            globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "rom_adopted", rom_id: rid } }));
            showToast(`${romName || "ROM"} is ready to play`);
        }
        catch (e) {
            detach(debugLog(`CustomPlayButton: adopt failed: ${e}`));
            showToast("Couldn't use the existing files — is RomM server running?");
        }
        finally {
            setActionPending(false);
        }
    };
    const handleCancelDownload = () => {
        if (romId == null)
            return;
        detach(cancelDownload(romId).catch(() => { }));
    };
    const handlePause = () => {
        if (romId == null)
            return;
        detach(pauseDownload(romId).catch(() => { }));
    };
    const handleResume = () => {
        if (romId == null)
            return;
        detach(resumeDownload(romId)
            .then((result) => {
            if (result.success)
                return;
            showToast(isTargetOccupied(result)
                ? "Something else is at this game's location now — cancel the download and start again"
                : result.message || "Couldn't resume the download");
        })
            .catch(() => showToast("Couldn't resume the download — is RomM server running?")));
    };
    const handleUninstall = async () => {
        if (!romId || uninstallPendingRef.current)
            return;
        uninstallPendingRef.current = true;
        const stateBeforeUninstall = state;
        setUninstallProgress(null);
        setState("uninstall_pending");
        detach(debugLog(`CustomPlayButton: uninstalling romId=${romId}`));
        try {
            const admission = capturePruneLeaseAdmission(leaseOwner);
            const result = await removeRom(romId);
            if (result.success) {
                await withPruneLease(result.prune_lease_token, "ROM uninstall", async (signal) => {
                    if (signal.aborted)
                        return;
                    await setLaunchOptionsConfirmed(appId, "").catch(() => false);
                }, leaseOwner, admission);
                globalThis.dispatchEvent(new CustomEvent("romm_rom_uninstalled", { detail: { rom_id: romId } }));
                showToast(`${romName || "ROM"} uninstalled`);
                setState("uninstalling");
                transitionTimerRef.current = setTimeout(() => enterDownloadState(), 500);
                return;
            }
            else {
                showToast(result.message || "Uninstall failed");
                setState(stateBeforeUninstall);
            }
        }
        catch {
            showToast("Uninstall failed");
            setState(stateBeforeUninstall);
        }
        finally {
            uninstallPendingRef.current = false;
            setUninstallProgress(null);
        }
    };
    const showDropdownMenu = (e) => {
        DFL.showContextMenu(SP_JSX.jsx(DFL.Menu, { label: "RomM Actions", children: SP_JSX.jsx(DFL.MenuItem, { tone: "destructive", onClick: () => {
                    detach(handleUninstall());
                }, children: "Uninstall" }, "uninstall") }), getEventTarget(e));
    };
    const showDownloadActionsMenu = (e, paused) => {
        DFL.showContextMenu(SP_JSX.jsxs(DFL.Menu, { label: "Download Actions", children: [paused ? (SP_JSX.jsx(DFL.MenuItem, { onClick: handleResume, children: "Resume" }, "resume")) : (SP_JSX.jsx(DFL.MenuItem, { onClick: handlePause, children: "Pause" }, "pause")), SP_JSX.jsx(DFL.MenuItem, { tone: "destructive", onClick: handleCancelDownload, children: "Cancel" }, "cancel")] }), getEventTarget(e));
    };
    if (state === "not_romm" || state === "loading") {
        detach(debugLog(`CustomPlayButton: returning null (state=${state})`));
        return null;
    }
    detach(debugLog(`CustomPlayButton: rendering state=${state}`));
    const dropdownArrowStyle = {
        height: "48px",
        width: "36px",
        minWidth: "36px",
        padding: 0,
        border: "none",
        borderRadius: "0 2px 2px 0",
        cursor: "pointer",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        borderLeft: "1px solid rgba(0, 0, 0, 0.2)",
    };
    const btnContainerStyle = {
        display: "flex",
        flexDirection: "row",
        width: "200px",
        height: "48px",
    };
    const mainBtnStyle = {
        height: "100%",
        flex: "1 1 auto",
        padding: "4px 12px",
        border: "none",
        color: "#fff",
        fontSize: "16px",
        fontWeight: "bold",
    };
    if (isRunning) {
        return (SP_JSX.jsxs(DFL.Focusable, { ref: containerRef, className: [appActionButtonClasses?.PlayButtonContainer, appActionButtonClasses?.Green]
                .filter(Boolean)
                .join(" "), style: btnContainerStyle, children: [SP_JSX.jsx(DFL.DialogButton, { className: [appActionButtonClasses?.PlayButton, "romm-btn-play"].filter(Boolean).join(" "), style: {
                        ...mainBtnStyle,
                        borderRadius: "2px 0 0 2px",
                        background: "linear-gradient(to right, #70d61d 0%, #01a75b 60%)",
                        backgroundPosition: "25%",
                        backgroundSize: "330% 100%",
                    }, onClick: () => {
                        detach(handleResumeGame());
                    }, onFocus: scrollToTop, children: "Resume" }), SP_JSX.jsx(DFL.DialogButton, { className: "romm-btn-cancel", "aria-label": "Game actions", title: "Game actions", style: {
                        ...dropdownArrowStyle,
                        background: "rgba(255, 255, 255, 0.15)",
                        color: "#fff",
                    }, onClick: (e) => showRunningActionsMenu(e), children: SP_JSX.jsx("svg", { width: "12", height: "8", viewBox: "0 0 12 8", fill: "none", xmlns: "http://www.w3.org/2000/svg", children: SP_JSX.jsx("path", { d: "M1 1.5L6 6.5L11 1.5", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" }) }) })] }));
    }
    if (state === "dl_complete") {
        return (SP_JSX.jsx(DFL.Focusable, { className: [appActionButtonClasses?.PlayButtonContainer, appActionButtonClasses?.Green]
                .filter(Boolean)
                .join(" "), style: btnContainerStyle, children: SP_JSX.jsx(DFL.DialogButton, { className: [appActionButtonClasses?.PlayButton, "romm-btn-play", "romm-dl-complete-flash"]
                    .filter(Boolean)
                    .join(" "), style: {
                    ...mainBtnStyle,
                    borderRadius: "2px",
                    background: "linear-gradient(to right, #80e62a, #01b866)",
                    filter: "brightness(1.2)",
                }, disabled: true, children: SP_JSX.jsx("span", { className: "romm-dl-label", children: "Ready!" }) }) }));
    }
    if (state === "download") {
        const t = dlProgress && dlProgress.totalBytes > 0 ? dlProgress.bytesDownloaded / dlProgress.totalBytes : 0;
        const downloading = actionPending && dlProgress;
        const paused = downloading ? dlProgress.paused : false;
        const resumable = downloading ? dlProgress.resumable : false;
        const extracting = downloading ? dlProgress.extracting : false;
        let fillColor;
        if (extracting) {
            fillColor = `linear-gradient(to right, rgb(${GREEN_LEFT.join(",")}), rgb(${GREEN_RIGHT.join(",")}))`;
        }
        else if (downloading) {
            fillColor = `linear-gradient(to right, ${lerpColor(BLUE_LEFT, GREEN_LEFT, t)}, ${lerpColor(BLUE_RIGHT, GREEN_RIGHT, t)})`;
        }
        else {
            fillColor = "linear-gradient(to right, #1a9fff, #0078d4)";
        }
        let pulseColor;
        if (paused) {
            pulseColor = "rgba(212,167,44,0.7)";
        }
        else if (extracting) {
            pulseColor = `rgb(${GREEN_LEFT.join(", ")})`;
        }
        else if (downloading) {
            pulseColor = lerpColor(BLUE_LEFT, GREEN_LEFT, t);
        }
        else {
            pulseColor = "rgba(26,159,255,0.7)";
        }
        let dlLabel;
        if (extracting) {
            dlLabel = `Extracting… ${Math.round(t * 100)}%`;
        }
        else if (paused) {
            dlLabel = "Paused";
        }
        else if (downloading) {
            dlLabel = formatProgress(dlProgress.bytesDownloaded, dlProgress.totalBytes);
        }
        else if (actionPending) {
            dlLabel = "Starting...";
        }
        else if (targetOccupied || candidatePresent) {
            dlLabel = "Use Existing Files";
        }
        else {
            dlLabel = "Download";
        }
        let baseBg;
        if (isOffline) {
            baseBg = "linear-gradient(to right, #6b7b8b, #5a6a7a)";
        }
        else if (extracting) {
            baseBg = "linear-gradient(to right, #1a4d1a, #0f3320)";
        }
        else if (downloading) {
            baseBg = `linear-gradient(to right, ${lerpColor([10, 50, 90], [5, 35, 65], t)}, ${lerpColor([5, 35, 65], [5, 50, 30], t)})`;
        }
        else {
            baseBg = "linear-gradient(to right, #1a9fff, #0078d4)";
        }
        const downloadBlockedByVanished = boundVanished && !downloading && !paused && !extracting;
        const downloadBtn = (SP_JSX.jsxs(DFL.DialogButton, { className: [appActionButtonClasses?.PlayButton, "romm-btn-download", !downloading && "romm-btn-download-idle"]
                .filter(Boolean)
                .join(" "), style: {
                ...mainBtnStyle,
                borderRadius: downloading ? "2px 0 0 2px" : "2px",
                background: baseBg,
            }, onClick: () => {
                detach(handleDownload());
            }, disabled: actionPending || isOffline || downloadBlockedByVanished, children: [downloading && (SP_JSX.jsx("div", { className: "romm-dl-fill", style: {
                        width: `${t * 100}%`,
                        background: fillColor,
                    } })), SP_JSX.jsx("span", { className: "romm-dl-label", children: dlLabel })] }));
        if (!downloading) {
            return (SP_JSX.jsx(DFL.Focusable, { ref: containerRef, className: appActionButtonClasses?.PlayButtonContainer, style: btnContainerStyle, children: downloadBtn }));
        }
        const cancelX = (SP_JSX.jsx(DFL.DialogButton, { className: "romm-btn-cancel", "aria-label": "Cancel download", title: "Cancel download", style: {
                ...dropdownArrowStyle,
                background: "rgba(255, 255, 255, 0.15)",
                color: "#fff",
            }, onClick: handleCancelDownload, children: SP_JSX.jsx("svg", { width: "12", height: "12", viewBox: "0 0 12 12", fill: "none", xmlns: "http://www.w3.org/2000/svg", children: SP_JSX.jsx("path", { d: "M1 1L11 11M11 1L1 11", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round" }) }) }));
        const dropdown = (SP_JSX.jsx(DFL.DialogButton, { className: "romm-btn-cancel", "aria-label": "Download actions", title: "Download actions", style: {
                ...dropdownArrowStyle,
                background: "rgba(255, 255, 255, 0.15)",
                color: "#fff",
            }, onClick: (e) => showDownloadActionsMenu(e, paused), children: SP_JSX.jsx("svg", { width: "12", height: "8", viewBox: "0 0 12 8", fill: "none", xmlns: "http://www.w3.org/2000/svg", children: SP_JSX.jsx("path", { d: "M1 1.5L6 6.5L11 1.5", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" }) }) }));
        const extractThrobber = (SP_JSX.jsx(DFL.DialogButton, { className: "romm-btn-cancel", "aria-label": "Extracting", title: "Extracting", style: {
                ...dropdownArrowStyle,
                background: "rgba(255, 255, 255, 0.15)",
                color: "#fff",
            }, disabled: true, children: SP_JSX.jsx("span", { className: `${appActionButtonClasses?.Throbber || ""} romm-throbber`.trim() }) }));
        let rightAction;
        if (extracting) {
            rightAction = extractThrobber;
        }
        else if (resumable) {
            rightAction = dropdown;
        }
        else {
            rightAction = cancelX;
        }
        return (SP_JSX.jsxs(DFL.Focusable, { ref: containerRef, className: [appActionButtonClasses?.PlayButtonContainer, "romm-dl-active-group"].filter(Boolean).join(" "), style: { ...btnContainerStyle, "--romm-pulse-color": pulseColor }, children: [downloadBtn, SP_JSX.jsx("div", { style: { display: "flex", flexDirection: "row", height: "100%" }, children: rightAction })] }));
    }
    if (state === "uninstall_pending") {
        return (SP_JSX.jsx(DFL.Focusable, { className: appActionButtonClasses?.PlayButtonContainer, style: btnContainerStyle, children: SP_JSX.jsx(DFL.DialogButton, { className: [appActionButtonClasses?.PlayButton, "romm-btn-download"].filter(Boolean).join(" "), style: {
                    ...mainBtnStyle,
                    borderRadius: "2px",
                    background: "linear-gradient(to right, #47b3ff, #1a9fff)",
                }, disabled: true, children: SP_JSX.jsx("span", { className: "romm-dl-label", children: uninstallProgress
                        ? `Uninstalling ${uninstallProgress.removed}/${uninstallProgress.total}`
                        : "Uninstalling..." }) }) }));
    }
    if (state === "uninstalling") {
        return (SP_JSX.jsx(DFL.Focusable, { className: appActionButtonClasses?.PlayButtonContainer, style: btnContainerStyle, children: SP_JSX.jsx(DFL.DialogButton, { className: [appActionButtonClasses?.PlayButton, "romm-btn-download", "romm-dl-uninstall-flash"]
                    .filter(Boolean)
                    .join(" "), style: {
                    ...mainBtnStyle,
                    borderRadius: "2px",
                    background: "linear-gradient(to right, #47b3ff, #1a9fff)",
                    filter: "brightness(1.3)",
                }, disabled: true, children: SP_JSX.jsx("span", { className: "romm-dl-label", children: "Uninstalled" }) }) }));
    }
    if (state === "launching") {
        return (SP_JSX.jsx(DFL.Focusable, { className: appActionButtonClasses?.PlayButtonContainer, style: btnContainerStyle, children: SP_JSX.jsxs(DFL.DialogButton, { className: [appActionButtonClasses?.PlayButton, "romm-btn-play", isOffline && "romm-offline"]
                    .filter(Boolean)
                    .join(" "), style: {
                    ...mainBtnStyle,
                    borderRadius: "2px",
                    background: "linear-gradient(to right, #70d61d 0%, #01a75b 60%)",
                    backgroundPosition: "25%",
                    backgroundSize: "330% 100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                }, disabled: true, children: [SP_JSX.jsx("span", { className: `${appActionButtonClasses?.Throbber || ""} romm-throbber`.trim() }), SP_JSX.jsx("span", { children: "Launching..." })] }) }));
    }
    if (state === "syncing") {
        return (SP_JSX.jsx(DFL.Focusable, { className: appActionButtonClasses?.PlayButtonContainer, style: btnContainerStyle, children: SP_JSX.jsxs(DFL.DialogButton, { className: [appActionButtonClasses?.PlayButton, "romm-btn-play", isOffline && "romm-offline"]
                    .filter(Boolean)
                    .join(" "), style: {
                    ...mainBtnStyle,
                    borderRadius: "2px",
                    background: "linear-gradient(to right, #70d61d 0%, #01a75b 60%)",
                    backgroundPosition: "25%",
                    backgroundSize: "330% 100%",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                }, disabled: true, children: [SP_JSX.jsx("span", { className: `${appActionButtonClasses?.Throbber || ""} romm-throbber`.trim() }), SP_JSX.jsx("span", { children: "Syncing saves..." })] }) }));
    }
    if (state === "conflict") {
        return (SP_JSX.jsx(DFL.Focusable, { ref: containerRef, className: appActionButtonClasses?.PlayButtonContainer, style: btnContainerStyle, children: SP_JSX.jsx(DFL.DialogButton, { className: [appActionButtonClasses?.PlayButton, "romm-btn-conflict"].filter(Boolean).join(" "), style: {
                    ...mainBtnStyle,
                    borderRadius: "2px",
                    background: "linear-gradient(to right, #d4a72c, #b8941f)",
                }, onClick: () => {
                    detach(handleResolveConflict());
                }, children: "Resolve Conflict" }) }));
    }
    const playBg = isOffline
        ? "linear-gradient(to right, #6b7b6b 0%, #5a6a5a 60%)"
        : "linear-gradient(to right, #70d61d 0%, #01a75b 60%)";
    const dropdownBg = isOffline
        ? "linear-gradient(to right, #5a6a5a, #4d5d4d)"
        : "linear-gradient(to right, #4da636, #3f8a2b)";
    return (SP_JSX.jsxs(DFL.Focusable, { ref: containerRef, className: [appActionButtonClasses?.PlayButtonContainer, !isOffline && appActionButtonClasses?.Green]
            .filter(Boolean)
            .join(" "), style: btnContainerStyle, children: [SP_JSX.jsx(DFL.DialogButton, { className: [appActionButtonClasses?.PlayButton, "romm-btn-play", isOffline && "romm-offline"]
                    .filter(Boolean)
                    .join(" "), style: {
                    ...mainBtnStyle,
                    borderRadius: "2px 0 0 2px",
                    background: playBg,
                    backgroundPosition: "25%",
                    backgroundSize: "330% 100%",
                }, onClick: () => {
                    detach(handlePlay());
                }, onFocus: scrollToTop, children: "Play" }), SP_JSX.jsx(DFL.DialogButton, { className: "romm-btn-dropdown", style: {
                    ...dropdownArrowStyle,
                    background: dropdownBg,
                }, onClick: showDropdownMenu, onFocus: scrollToTop, children: SP_JSX.jsx("svg", { width: "12", height: "8", viewBox: "0 0 12 8", fill: "none", xmlns: "http://www.w3.org/2000/svg", children: SP_JSX.jsx("path", { d: "M1 1.5L6 6.5L11 1.5", stroke: "currentColor", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" }) }) })] }));
};

const DISC_GREY = "#dcdedf";
const DISC_ACCENT = "#59b6ff";
const DiscStack = ({ size, color }) => {
    const step = Math.round(size * 0.3);
    return (SP_JSX.jsxs("span", { style: { position: "relative", display: "inline-block", width: size + step, height: size + step, color }, children: [SP_JSX.jsx(FaCompactDisc, { size: size, style: { position: "absolute", left: step, top: step, opacity: 0.55 } }), SP_JSX.jsx(FaCompactDisc, { size: size, style: { position: "absolute", left: 0, top: 0, opacity: 1 } })] }));
};
const DiscWithNumber = ({ size, color, num }) => (SP_JSX.jsxs("span", { style: { display: "inline-flex", alignItems: "center", gap: "4px", color }, children: [SP_JSX.jsx(FaCompactDisc, { size: size }), SP_JSX.jsx("span", { style: { fontWeight: 600, fontSize: `${Math.round(size * 0.6)}px` }, children: num })] }));
const DiscSelector = ({ appId }) => {
    const leaseOwner = `disc-selector:${appId}`;
    const [selection, setSelection] = SP_REACT.useState(null);
    const [selected, setSelected] = SP_REACT.useState(null);
    const romIdRef = SP_REACT.useRef(null);
    const fetchSelection = async (rid) => {
        try {
            const result = await getDiscSelection(rid);
            setSelection(result);
            setSelected(result.selected ?? null);
        }
        catch (e) {
            logError(`DiscSelector: getDiscSelection failed: ${e}`);
        }
    };
    SP_REACT.useEffect(() => {
        mountPruneLeaseOwner(leaseOwner);
        let cancelled = false;
        async function init() {
            try {
                const cached = await getCachedGameDetail(appId);
                if (cancelled || !cached.found || cached.rom_id == null)
                    return;
                romIdRef.current = cached.rom_id;
                if (!cached.installed)
                    return;
                await fetchSelection(cached.rom_id);
            }
            catch (e) {
                logError(`DiscSelector init error: ${e}`);
            }
        }
        detach(init());
        return () => {
            cancelled = true;
            detach(releasePruneLeasesByOwner(leaseOwner));
        };
    }, [appId, leaseOwner]);
    SP_REACT.useEffect(() => {
        const completeListener = addEventListener("download_complete", (evt) => {
            if (evt.rom_id !== romIdRef.current)
                return;
            detach(fetchSelection(evt.rom_id));
        });
        const onUninstall = (e) => {
            const rid = e.detail?.rom_id;
            if (rid !== romIdRef.current)
                return;
            setSelection(null);
            setSelected(null);
        };
        globalThis.addEventListener("romm_rom_uninstalled", onUninstall);
        return () => {
            removeEventListener("download_complete", completeListener);
            globalThis.removeEventListener("romm_rom_uninstalled", onUninstall);
        };
    }, []);
    const handleChange = async (data) => {
        const rid = romIdRef.current;
        if (rid == null)
            return;
        const admission = capturePruneLeaseAdmission(leaseOwner);
        try {
            const result = await selectDisc(rid, data);
            await withPruneLease(result.prune_lease_token, "DiscSelector", async (signal) => {
                if (result.success) {
                    if (result.launch_options !== undefined) {
                        if (signal.aborted)
                            return;
                        await setLaunchOptionsConfirmed(appId, result.launch_options);
                    }
                    if (signal.aborted)
                        return;
                    setSelected(result.selected ?? null);
                }
                else {
                    showToast(result.message || "Failed to select disc");
                }
            }, leaseOwner, admission);
        }
        catch (e) {
            if (isPruneLeaseCancellation(e, admission)) {
                logWarn(`DiscSelector: disc selection continuation was cancelled: ${e}`);
                return;
            }
            logError(`DiscSelector: selectDisc failed: ${e}`);
            showToast("Failed to select disc");
        }
    };
    if (!selection?.multi_disc || !selection.discs || !selection.default)
        return null;
    const { discs, default: dflt } = selection;
    const isM3u = dflt.kind === "m3u";
    const effectiveSelected = selected ?? (isM3u ? null : dflt.filename);
    const isPinned = selected !== null;
    const showPlaylistFace = isM3u && selected === null;
    const activeDisc = discs.find((d) => d.filename === effectiveSelected);
    const activeNum = activeDisc ? (activeDisc.label.match(/\d+/)?.[0] ?? String(activeDisc.index)) : "";
    const options = [];
    if (isM3u)
        options.push({ data: null, icon: SP_JSX.jsx(DiscStack, { size: 16, color: DISC_GREY }), text: dflt.label });
    for (const disc of discs)
        options.push({ data: disc.filename, icon: SP_JSX.jsx(FaCompactDisc, { size: 16 }), text: disc.label });
    const openMenu = (e) => {
        DFL.showContextMenu(SP_JSX.jsx(DFL.Menu, { label: "Disc", children: options.map((o) => {
                const active = o.data === effectiveSelected;
                return (SP_JSX.jsx(DFL.MenuItem, { onClick: () => detach(handleChange(o.data)), children: SP_JSX.jsxs("span", { style: {
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "10px",
                            color: active ? DISC_ACCENT : undefined,
                        }, children: [o.icon, SP_JSX.jsx("span", { children: o.text }), active ? SP_JSX.jsx("span", { style: { marginLeft: "6px", fontWeight: 700 }, children: "\u2713" }) : null] }) }, String(o.data)));
            }) }), getEventTarget(e));
    };
    return (SP_JSX.jsxs(DFL.DialogButton, { className: "romm-disc-btn", onClick: openMenu, children: [showPlaylistFace ? (SP_JSX.jsx(DiscStack, { size: 22, color: DISC_GREY })) : (SP_JSX.jsx(DiscWithNumber, { size: 22, color: isPinned ? DISC_ACCENT : DISC_GREY, num: activeNum })), SP_JSX.jsx(FaChevronDown, { size: 10, color: "#cfd3d8" })] }));
};

async function applyCommittedVersionSwitch(result, onCover, admission) {
    return withPruneLease(result.prune_lease_token, "Version switch", async (signal) => {
        let confirmed = false;
        if (isPruneLeaseCancelled(signal))
            return confirmed;
        try {
            confirmed = await setLaunchOptionsConfirmed(result.app_id, result.launch_options);
        }
        catch (e) {
            logError(`Version switch: launch-options confirm threw for rom ${result.rom_id} (appId ${result.app_id}): ${e}`);
        }
        if (!confirmed) {
            logError(`Version switch: could not confirm launch options for rom ${result.rom_id} (appId ${result.app_id})`);
        }
        if (!isPruneLeaseCancelled(signal)) {
            await publishCommittedVersionSwitch(result.app_id, result.rom_id, onCover, signal);
        }
        return confirmed;
    }, `version-picker:${result.app_id}`, admission);
}
async function publishCommittedVersionSwitch(appId, romId, onCover, signal) {
    try {
        const cover = await fetchCoverBase64(romId);
        if (signal?.aborted)
            return;
        if (cover.base64) {
            onCover?.(romId, cover.base64);
            await SteamClient.Apps.SetCustomArtworkForApp(appId, cover.base64, "png", 0);
        }
    }
    catch (e) {
        logWarn(`Version switch: cover apply after switch failed for rom ${romId}: ${e}`);
    }
    if (signal?.aborted)
        return;
    invalidateCachedGameDetail(appId);
    globalThis.dispatchEvent(new CustomEvent("romm_data_changed", {
        detail: { type: "version_switched", app_id: appId, rom_id: romId },
    }));
}

function showUnsyncedSavesModal({ versionName, serverReachable, }) {
    return new Promise((resolve) => {
        const description = serverReachable
            ? `"${versionName}" has save changes that were never uploaded to RomM. They stay on disk, but won't sync until you switch back.`
            : `"${versionName}" has save changes that were never uploaded, and RomM is not reachable right now — so they can't be synced first. They stay on disk, but won't sync until you switch back.`;
        const middleButton = serverReachable
            ? { strMiddleButtonText: "Switch anyway", onMiddleButton: () => resolve("switch_anyway") }
            : {};
        DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Unsynced saves", strDescription: description, strOKButtonText: serverReachable ? "Sync now & switch" : "Switch anyway", strCancelButtonText: "Cancel", onOK: () => resolve(serverReachable ? "sync_and_switch" : "switch_anyway"), onCancel: () => resolve("cancel"), ...middleButton }));
    });
}

const LOST_RESULT_TIMEOUT_MS = 15 * 60000;
let activeRunId = null;
let activePreviewId = null;
let progress = null;
let complete = null;
const receivedChunks = new Map();
let terminalChunkIndex = null;
let pendingPreviewId = null;
let resultLost = false;
let lostResultTimer = null;
const listeners$1 = new Set();
function notify() {
    for (const listener of listeners$1)
        listener();
}
function disarmLostResultTimer() {
    if (lostResultTimer === null)
        return;
    clearTimeout(lostResultTimer);
    lostResultTimer = null;
}
function armLostResultTimer() {
    disarmLostResultTimer();
    lostResultTimer = setTimeout(() => {
        lostResultTimer = null;
        if (complete !== null)
            return;
        pendingPreviewId = activePreviewId;
        activeRunId = null;
        progress = null;
        resultLost = true;
        notify();
    }, LOST_RESULT_TIMEOUT_MS);
}
function unique(values) {
    return [...new Set(values)].sort((a, b) => a - b);
}
function beginPruneRun(runId, previewId) {
    if (activeRunId === runId)
        return true;
    if (pendingPreviewId !== previewId)
        return false;
    activeRunId = runId;
    activePreviewId = previewId;
    pendingPreviewId = null;
    progress = null;
    complete = null;
    receivedChunks.clear();
    terminalChunkIndex = null;
    resultLost = false;
    armLostResultTimer();
    notify();
    return true;
}
function admitPruneFrame(previewId, runId) {
    if (complete !== null)
        return false;
    if (activeRunId !== null)
        return activeRunId === runId;
    if (pendingPreviewId === null || pendingPreviewId !== previewId)
        return false;
    activeRunId = runId;
    activePreviewId = previewId;
    pendingPreviewId = null;
    resultLost = false;
    armLostResultTimer();
    notify();
    return true;
}
function setPruneProgress(value) {
    if (!admitPruneFrame(value.preview_id, value.run_id))
        return;
    progress = value;
    armLostResultTimer();
    notify();
}
function setPruneComplete(value) {
    if (!admitPruneFrame(value.preview_id, value.run_id))
        return null;
    const chunkIndex = value.chunk_index ?? 0;
    if (receivedChunks.has(chunkIndex))
        return null;
    receivedChunks.set(chunkIndex, value);
    if (value.final !== false)
        terminalChunkIndex = chunkIndex;
    armLostResultTimer();
    if (terminalChunkIndex === null)
        return null;
    for (let index = 0; index <= terminalChunkIndex; index++) {
        if (!receivedChunks.has(index))
            return null;
    }
    disarmLostResultTimer();
    const chunks = Array.from({ length: terminalChunkIndex + 1 }, (_, index) => receivedChunks.get(index));
    const terminal = receivedChunks.get(terminalChunkIndex);
    progress = null;
    complete = {
        ...terminal,
        removed_rom_ids: unique(chunks.flatMap((chunk) => chunk.removed_rom_ids)),
        affected_app_ids: unique(chunks.flatMap((chunk) => chunk.affected_app_ids)),
        removed_app_ids: unique(chunks.flatMap((chunk) => chunk.removed_app_ids ?? [])),
        results: chunks.flatMap((chunk) => chunk.results),
    };
    notify();
    return complete;
}
function getPruneState() {
    return { runId: activeRunId, progress, complete };
}
function isPruneResultLost() {
    return resultLost;
}
function onPruneStateChange(listener) {
    listeners$1.add(listener);
    return () => listeners$1.delete(listener);
}
function beginPrunePreview(previewId) {
    disarmLostResultTimer();
    activeRunId = null;
    activePreviewId = null;
    progress = null;
    complete = null;
    receivedChunks.clear();
    terminalChunkIndex = null;
    pendingPreviewId = previewId;
    resultLost = false;
    notify();
}

const PAGE_SIZE = 50;
const SELECTION_PAGE_SIZE = 100;
const PRUNE_CALLABLE_TIMEOUT_MS = 15000;
const RESULT_LOST_MESSAGE = "The cleanup result was lost — check your library and run the scan again.";
const CANCEL_HINT = "Stops before the next game. The one being processed now finishes and reports what it changed.";
const CANCELLING_HINT = "Stopping — finishing the current safe step, then reporting what changed.";
async function requestPruneCancel(runId) {
    logInfo(`[prune] Cancel pressed for run ${runId}`);
    try {
        const result = await withTimeout(cancelPrune(runId), PRUNE_CALLABLE_TIMEOUT_MS);
        if (!result.success) {
            logWarn(`[prune] cancelPrune refused: reason=${result.reason ?? "none"}`);
            return result.message;
        }
        logInfo(`[prune] cancelPrune accepted for run ${runId}`);
        return null;
    }
    catch (e) {
        logError(`[prune] cancelPrune threw for run ${runId}: ${e}`);
        return `Could not request cancellation: ${e}`;
    }
}
const plural = (count, singular, pluralForm) => (count === 1 ? singular : pluralForm);
function formatBytes(bytes) {
    if (bytes < 1024)
        return `${bytes} B`;
    const units = ["KiB", "MiB", "GiB", "TiB"];
    let value = bytes / 1024;
    let index = 0;
    while (value >= 1024 && index < units.length - 1) {
        value /= 1024;
        index++;
    }
    return `${value.toFixed(value >= 10 ? 1 : 2)} ${units[index]}`;
}
const STAGE_LABELS = {
    checking: "Checking with RomM",
    creating_recovery: "Backing up",
    recovery_sealed: "Backup complete",
    repointing: "Updating the Steam shortcut",
    removing_shortcut: "Removing the Steam shortcut",
    removing: "Removing local data",
    removed: "Done",
};
function stageLabel(stage) {
    return STAGE_LABELS[stage] ?? stage.replace(/_/g, " ");
}
function finishedGroupsPercent(current, total) {
    return Math.min(100, Math.max(0, ((current - 1) / total) * 100));
}
const CleanupProgress = ({ progress }) => (SP_JSX.jsxs("div", { style: { width: "100%" }, children: [SP_JSX.jsxs("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "flex-start", fontSize: "12px" }, children: [SP_JSX.jsxs("span", { style: { overflowWrap: "anywhere" }, children: [stageLabel(progress.stage), " \u2014 ", progress.name] }), SP_JSX.jsxs("span", { style: { flexShrink: 0, marginLeft: "8px" }, children: [progress.current, " / ", progress.total] })] }), SP_JSX.jsx(DFL.ProgressBar, { indeterminate: progress.total <= 0, ...(progress.total > 0 ? { nProgress: finishedGroupsPercent(progress.current, progress.total) } : {}) })] }));
const FinishedCleanupBar = () => SP_JSX.jsx(DFL.ProgressBar, { nProgress: 100 });
function removedInGroup(item) {
    return item.removed_count ?? item.removed_rom_ids?.length ?? 0;
}
function requestFor(scope, romId, previewId, offset) {
    return { scope, rom_id: romId, preview_id: previewId, offset, limit: PAGE_SIZE };
}
function confirmBlockedReason(state) {
    if (state.completed)
        return null;
    if (state.runInFlight)
        return "A cleanup is already running.";
    if (!state.allEntriesLoaded)
        return `Load all ${state.total} entries before confirming.`;
    if (!state.destructiveConfirmed)
        return "Confirm you understand there will be no recovery bundle.";
    if (state.insufficientSpace) {
        return state.unknownSelectedSize
            ? "A selected ROM's size can't be measured, so the recovery bundle can't be guaranteed to fit."
            : "The selected ROM content doesn't fit in the free space at the recovery target.";
    }
    if (!state.anyOptionChosen)
        return "Choose at least one cleanup option above.";
    return null;
}
async function stageInstalledSelections(previewId, selected, setStatus) {
    let selectionId = null;
    for (let offset = 0; offset < selected.length; offset += SELECTION_PAGE_SIZE) {
        const page = selected.slice(offset, offset + SELECTION_PAGE_SIZE);
        const staged = await withTimeout(stagePruneInstalledSelection({
            preview_id: previewId,
            selection_id: selectionId,
            rom_ids: page,
            final: offset + page.length >= selected.length,
        }), PRUNE_CALLABLE_TIMEOUT_MS);
        if (!staged.success || !staged.selection_id) {
            setStatus(staged.message ?? "Installed-content selections could not be staged.");
            logWarn(`[prune] Confirm aborted while staging installed content: ${staged.message ?? "no message"}`);
            return { ok: false };
        }
        selectionId = staged.selection_id;
    }
    return { ok: true, selectionId };
}
function confirmButtonLabel(starting, progress) {
    if (starting)
        return "Starting...";
    if (progress)
        return `${progress.stage.replace(/_/g, " ")}...`;
    return "Confirm Cleanup";
}
function scanButtonDescription(syncRunning, runActive) {
    if (syncRunning)
        return "Unavailable while a library sync is running.";
    if (runActive)
        return "A cleanup is running. Its progress is shown below.";
    return undefined;
}
const CleanupModal = ({ initial, scope, romId, closeModal }) => {
    const [items, setItems] = SP_REACT.useState(initial.items ?? []);
    const [loadingMore, setLoadingMore] = SP_REACT.useState(false);
    const [starting, setStarting] = SP_REACT.useState(false);
    const [cancelRequestedFor, setCancelRequestedFor] = SP_REACT.useState(null);
    const [runStarted, setRunStarted] = SP_REACT.useState(false);
    const [status, setStatus] = SP_REACT.useState("");
    const [repoint, setRepoint] = SP_REACT.useState(true);
    const [removeRows, setRemoveRows] = SP_REACT.useState(true);
    const [removeDeadGames, setRemoveDeadGames] = SP_REACT.useState(true);
    const [recovery, setRecovery] = SP_REACT.useState(true);
    const [confirmWithoutRecovery, setConfirmWithoutRecovery] = SP_REACT.useState(false);
    const [includedContent, setIncludedContent] = SP_REACT.useState(new Set());
    const [freeBytes, setFreeBytes] = SP_REACT.useState(initial.free_bytes ?? 0);
    const [pruneState, setPruneState] = SP_REACT.useState(getPruneState());
    const [resultLost, setResultLost] = SP_REACT.useState(isPruneResultLost());
    SP_REACT.useEffect(() => {
        const unsubscribe = onPruneStateChange(() => {
            setPruneState(getPruneState());
            setResultLost(isPruneResultLost());
        });
        return () => {
            unsubscribe();
        };
    }, []);
    const total = initial.total ?? items.length;
    const candidateTotal = initial.candidate_total ?? total;
    const visibleItems = removeDeadGames ? items : items.filter((item) => item.candidate);
    const selectedBytes = visibleItems.reduce((sum, item) => sum + (includedContent.has(item.rom_id) ? (item.installed_bytes ?? 0) : 0), 0);
    const unknownSelectedSize = visibleItems.some((item) => includedContent.has(item.rom_id) && item.installed && item.installed_bytes === null);
    const insufficientSpace = recovery && (unknownSelectedSize || selectedBytes > freeBytes);
    const destructiveConfirmed = recovery || confirmWithoutRecovery;
    const allEntriesLoaded = items.length === total;
    const progress = pruneState.progress;
    const complete = pruneState.complete;
    const runInFlight = complete === null && (starting || pruneState.runId !== null);
    const cancelling = complete === null && cancelRequestedFor !== null && cancelRequestedFor === pruneState.runId;
    const blockedReason = confirmBlockedReason({
        completed: complete !== null,
        runInFlight,
        allEntriesLoaded,
        total,
        destructiveConfirmed,
        insufficientSpace,
        unknownSelectedSize,
        anyOptionChosen: repoint || removeRows || removeDeadGames,
    });
    const pressBlocked = complete !== null || runInFlight;
    const toggleContent = (romIdToToggle, checked) => {
        setIncludedContent((current) => {
            const next = new Set(current);
            if (checked)
                next.add(romIdToToggle);
            else
                next.delete(romIdToToggle);
            return next;
        });
    };
    const loadMore = async () => {
        if (!initial.preview_id || items.length >= total)
            return;
        setLoadingMore(true);
        try {
            const next = await withTimeout(getPrunePreview(requestFor(scope, romId, initial.preview_id, items.length)), PRUNE_CALLABLE_TIMEOUT_MS);
            if (!next.success) {
                setStatus(next.message ?? "Could not load more candidates.");
                return;
            }
            setItems((current) => [...current, ...(next.items ?? [])]);
            if (typeof next.free_bytes === "number")
                setFreeBytes(next.free_bytes);
        }
        catch (e) {
            setStatus(`Could not load more candidates: ${e}`);
        }
        finally {
            setLoadingMore(false);
        }
    };
    const refreshFreeSpace = async () => {
        if (!initial.preview_id)
            return;
        try {
            const refreshed = await withTimeout(getPrunePreview({
                scope,
                rom_id: romId,
                preview_id: initial.preview_id,
                offset: 0,
                limit: 0,
            }), PRUNE_CALLABLE_TIMEOUT_MS);
            if (!refreshed.success || typeof refreshed.free_bytes !== "number") {
                setStatus(refreshed.message ?? "Could not refresh recovery space.");
                return;
            }
            setFreeBytes(refreshed.free_bytes);
        }
        catch (e) {
            setStatus(`Could not refresh recovery space: ${e}`);
        }
    };
    const start = async () => {
        logInfo(`[prune] Confirm pressed (preview=${initial.preview_id ?? "none"}, scope=${scope}, total=${total})`);
        if (!initial.preview_id) {
            setStatus("This cleanup preview has no id — close and scan again.");
            logError("[prune] Confirm aborted: the modal holds no preview id");
            return;
        }
        if (blockedReason !== null) {
            setStatus(`Cleanup did not start: ${blockedReason}`);
            logWarn(`[prune] Confirm refused locally: ${blockedReason}`);
            return;
        }
        setStarting(true);
        setStatus(includedContent.size
            ? `Staging ${includedContent.size} installed-content selection(s)...`
            : "Starting cleanup...");
        try {
            const staged = await stageInstalledSelections(initial.preview_id, [...includedContent], setStatus);
            if (!staged.ok)
                return;
            const result = await withTimeout(startPrune({
                preview_id: initial.preview_id,
                confirmed: true,
                repoint_shortcuts: repoint,
                remove_rows: removeRows,
                remove_fully_vanished: removeDeadGames,
                create_recovery_bundle: recovery,
                installed_selection_id: staged.selectionId,
            }), PRUNE_CALLABLE_TIMEOUT_MS);
            if (!result.success) {
                setStatus(result.message ?? "Cleanup could not start.");
                logWarn(`[prune] startPrune refused: reason=${result.reason ?? "none"} message=${result.message ?? "none"}`);
                return;
            }
            if (!result.run_id) {
                setStatus("Cleanup started but the backend response carried no run id.");
                logError("[prune] startPrune reported success with no run id");
                return;
            }
            setRunStarted(true);
            if (!beginPruneRun(result.run_id, initial.preview_id)) {
                setStatus("Cleanup started, but this dialog lost track of it. Check the log, then re-scan to see the result.");
                logError(`[prune] run ${result.run_id} started but preview ${initial.preview_id} was no longer pending`);
                return;
            }
            setStatus("Cleanup running...");
            logInfo(`[prune] startPrune accepted: run=${result.run_id}`);
        }
        catch (e) {
            const adopted = getPruneState();
            if (adopted.runId !== null) {
                setRunStarted(true);
                setStatus(adopted.complete ? "Cleanup completed." : "Cleanup running...");
                logWarn(`[prune] startPrune response was lost; adopted run ${adopted.runId} from its frames instead: ${e}`);
            }
            else {
                setStatus(`Cleanup could not start: ${e}`);
                logError(`[prune] startPrune threw with no run adopted: ${e}`);
            }
        }
        finally {
            setStarting(false);
        }
    };
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: closeModal, children: SP_JSX.jsxs("div", { style: {
                minWidth: "440px",
                maxWidth: "720px",
                padding: "18px",
                paddingBottom: "28px",
                maxHeight: "76vh",
                overflowY: "auto",
            }, children: [SP_JSX.jsx("div", { style: { fontSize: "20px", fontWeight: 700, marginBottom: "6px" }, children: "Clean Up Removed RomM Games" }), SP_JSX.jsxs("div", { style: { color: "#c7d5e0", marginBottom: "14px" }, children: [`${candidateTotal} locally kept ${plural(candidateTotal, "version", "versions")}${scope === "bulk" ? "" : " of this game"} ${plural(candidateTotal, "is", "are")} no longer on your RomM server.`, " ", "Nothing is removed until each one is checked against the server again \u2014 only entries RomM confirms as gone can be deleted.", removeDeadGames && total > candidateTotal
                            ? " Other versions of the same games are listed below; they stay, unless the check finds every version of a game gone."
                            : ""] }), SP_JSX.jsxs("div", { children: [SP_JSX.jsx("div", { onFocus: scrollNearestToTop, children: SP_JSX.jsx(DFL.ToggleField, { label: "Repoint vanished shortcuts to the live default version", checked: repoint, disabled: runInFlight, onChange: setRepoint }) }), SP_JSX.jsx(DFL.ToggleField, { label: "Remove confirmed rows and installed content from groups with a live version", checked: removeRows, disabled: runInFlight, onChange: setRemoveRows }), SP_JSX.jsx(DFL.ToggleField, { label: "Remove fully vanished games, including any Steam shortcut", description: "Only for games where the server confirms every single version is gone \u2014 those are removed whole, Steam shortcut included. The recovery bundle keeps the shortcut's Steam details so you can rebuild it by hand.", checked: removeDeadGames, disabled: runInFlight, onChange: (checked) => {
                                setRemoveDeadGames(checked);
                                if (!checked) {
                                    setIncludedContent((current) => {
                                        const stillShown = new Set(items.filter((item) => item.candidate).map((item) => item.rom_id));
                                        return new Set([...current].filter((romId) => stillShown.has(romId)));
                                    });
                                }
                            } }), SP_JSX.jsx(DFL.ToggleField, { label: "Create recovery bundle", description: `Verified bundles are sealed under ${initial.recovery_root ?? "the recovery directory"}.`, checked: recovery, disabled: runInFlight, onChange: (checked) => {
                                setRecovery(checked);
                                if (checked)
                                    setConfirmWithoutRecovery(false);
                                else
                                    setIncludedContent(new Set());
                            } }), !recovery && (SP_JSX.jsx(DFL.ToggleField, { label: "I understand local database state and playtime will have no recovery bundle", checked: confirmWithoutRecovery, disabled: runInFlight, onChange: setConfirmWithoutRecovery })), SP_JSX.jsx("div", { style: { margin: "14px 0 8px", fontWeight: 700 }, children: "Versions no longer on RomM" }), visibleItems.map((item, index) => (SP_JSX.jsxs(SP_REACT.Fragment, { children: [!item.candidate && (index === 0 || visibleItems[index - 1].candidate) && (SP_JSX.jsx("div", { style: { margin: "18px 0 8px", fontWeight: 700 }, children: "Other versions of these games \u2014 kept" })), SP_JSX.jsxs("div", { style: {
                                        padding: "10px 0",
                                        borderTop: "1px solid rgba(255,255,255,0.10)",
                                        ...(item.candidate ? {} : { paddingLeft: "14px", opacity: 0.75 }),
                                    }, children: [SP_JSX.jsx("div", { style: { fontWeight: item.candidate ? 600 : 400 }, children: item.name || item.fs_name || `ROM ${item.rom_id}` }), (item.name_truncated ||
                                            item.fs_name_truncated ||
                                            item.group_id_truncated ||
                                            item.warning_truncated) && (SP_JSX.jsx("div", { style: { color: "#e5a43b", fontSize: "12px" }, children: "One or more display fields were shortened to keep this preview page within the Decky wire limit." })), SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "#8f98a0" }, children: [item.platform_slug, " \u00B7 ROM ", item.rom_id, item.group_size > 1 ? ` · one of ${item.group_size} versions of this game` : ""] }), SP_JSX.jsx("div", { style: { fontSize: "12px", color: item.candidate ? "#c7d5e0" : "#8f98a0" }, children: item.candidate
                                                ? "Gone from RomM — removed once the server confirms it."
                                                : "Still on RomM at your last sync. Removed only if the final check finds every version of this game gone — then the whole game goes, Steam shortcut included." }), item.warning && SP_JSX.jsx("div", { style: { color: "#e5a43b", fontSize: "12px" }, children: item.warning }), item.installed && (SP_JSX.jsx(DFL.ToggleField, { label: `Include installed ROM content (${item.installed_bytes === null ? "size unavailable" : formatBytes(item.installed_bytes)})`, checked: includedContent.has(item.rom_id), disabled: runInFlight || !recovery, onChange: (checked) => toggleContent(item.rom_id, checked) })), item.installed && (!recovery || !includedContent.has(item.rom_id)) && (SP_JSX.jsx("div", { style: { color: "#e5a43b", fontSize: "12px" }, children: "Without a backup, the downloaded ROM file is deleted along with this version." }))] })] }, item.rom_id))), allEntriesLoaded && !visibleItems.some((item) => item.installed) && (SP_JSX.jsx("div", { style: { padding: "10px 0", fontSize: "12px", color: "#8f98a0" }, children: "None of these versions has ROM files downloaded on this device, so there is nothing to back up." })), items.length < total && (SP_JSX.jsx(DFL.DialogButton, { disabled: loadingMore, onClick: () => detach(loadMore()), children: loadingMore ? "Loading..." : `Load more (${items.length} of ${total})` })), !allEntriesLoaded && (SP_JSX.jsx("div", { style: { color: "#ff8c6a", fontSize: "12px", marginTop: "8px" }, children: "Load every page before confirming so all potentially removed group members and installed content are disclosed." }))] }), SP_JSX.jsxs("div", { style: { marginTop: "14px", padding: "10px", background: "rgba(0,0,0,0.20)" }, children: ["Selected ROM-content recovery estimate: ", formatBytes(selectedBytes), " \u00B7 Free at target:", " ", formatBytes(freeBytes), SP_JSX.jsx("div", { style: { color: "#8f98a0", fontSize: "12px", marginTop: "4px" }, children: "This is a lower bound. The backend remeasures mandatory saves, histories, caches, and Steam files before any mutation." }), SP_JSX.jsx("div", { style: { color: "#8f98a0", fontSize: "12px", marginTop: "4px" }, children: "Large installed-content selections are staged in bounded pages before cleanup; every checked item remains part of this run." }), SP_JSX.jsx(DFL.DialogButton, { disabled: runInFlight, onClick: () => detach(refreshFreeSpace()), children: "Refresh free space" }), insufficientSpace && (SP_JSX.jsx("div", { style: { color: "#ff8c6a", marginTop: "4px" }, children: unknownSelectedSize ? "A selected installed ROM has no safe measurable size." : "Not enough free space." }))] }), progress && (SP_JSX.jsxs("div", { style: { marginTop: "10px", color: "#c7d5e0" }, children: [SP_JSX.jsx("div", { role: "status", "aria-live": "polite", children: SP_JSX.jsx(CleanupProgress, { progress: progress }) }), SP_JSX.jsx("div", { style: { color: "#8f98a0", fontSize: "12px", marginTop: "4px" }, children: CANCEL_HINT }), SP_JSX.jsx(DFL.DialogButton, { disabled: cancelling, onClick: () => detach((async () => {
                                setCancelRequestedFor(progress.run_id);
                                const failure = await requestPruneCancel(progress.run_id);
                                if (failure !== null) {
                                    setCancelRequestedFor(null);
                                    setStatus(failure);
                                }
                            })()), children: cancelling ? "Stopping..." : "Stop Cleanup" }), cancelling && (SP_JSX.jsx("div", { role: "status", "aria-live": "polite", style: { color: "#8f98a0", fontSize: "12px", marginTop: "4px" }, children: CANCELLING_HINT }))] })), complete && (SP_JSX.jsxs("div", { style: { marginTop: "10px", color: complete.success ? "#8fd18b" : "#ffcc66" }, children: [SP_JSX.jsx(FinishedCleanupBar, {}), SP_JSX.jsxs("div", { role: "status", "aria-live": "polite", children: [complete.removed_count ?? complete.removed_rom_ids.length, " removed;", " ", complete.problem_count ??
                                    complete.results.filter((item) => ["partial", "failed", "skipped"].includes(item.status)).length, " ", "skipped, partial, or failed."] }), SP_JSX.jsxs(DFL.Focusable, { role: "region", "aria-label": "Cleanup details", tabIndex: 0, style: { maxHeight: "180px", overflowY: "auto", marginTop: "6px" }, children: [complete.message && (SP_JSX.jsxs("div", { style: { fontSize: "12px", marginTop: "4px" }, children: [complete.reason ? `${complete.reason}: ` : "", complete.message] })), complete.results
                                    .filter((item) => ["partial", "failed", "skipped"].includes(item.status) ||
                                    (item.warnings?.length ?? 0) > 0 ||
                                    item.warnings_omitted ||
                                    item.warnings_truncated ||
                                    (item.bundle_path !== undefined && removedInGroup(item) === 0))
                                    .map((item) => (SP_JSX.jsxs("div", { style: { fontSize: "12px", marginTop: "4px" }, children: [item.name || item.group_id, ": ", item.message, item.bundle_path !== undefined && removedInGroup(item) === 0 && (SP_JSX.jsxs("div", { children: ["Backup created, nothing removed. The folder stays at ", item.bundle_path, "."] })), item.message_truncated && SP_JSX.jsx("div", { children: "Detail was shortened to fit the Decky wire limit." }), item.warnings?.map((warning) => (SP_JSX.jsxs("div", { children: ["Warning: ", warning] }, warning))), item.warnings_omitted && (item.warning_count ?? 0) > (item.warnings?.length ?? 0) && (SP_JSX.jsxs("div", { children: [(item.warning_count ?? 0) - (item.warnings?.length ?? 0), " additional warning(s) omitted."] })), item.warnings_truncated && SP_JSX.jsx("div", { children: "One or more displayed warnings were shortened." })] }, item.group_id)))] })] })), resultLost && (SP_JSX.jsx("div", { role: "status", "aria-live": "polite", style: { marginTop: "10px", color: "#ff8c6a" }, children: RESULT_LOST_MESSAGE })), status && !complete && (SP_JSX.jsx("div", { role: "status", "aria-live": "polite", style: { marginTop: "10px", color: "#ffcc66" }, children: status })), blockedReason !== null && !runInFlight && (SP_JSX.jsx("div", { style: { marginTop: "10px", color: "#ff8c6a", fontSize: "12px" }, children: blockedReason })), SP_JSX.jsxs("div", { style: { display: "flex", justifyContent: "flex-end", gap: "10px", marginTop: "16px" }, children: [SP_JSX.jsx(DFL.DialogButton, { disabled: starting && complete === null, onClick: () => closeModal?.(), children: runStarted || complete !== null ? "Close" : "Cancel" }), SP_JSX.jsx(DFL.DialogButton, { disabled: pressBlocked, onClick: () => detach(start()), children: confirmButtonLabel(starting, progress) })] })] }) }));
};
async function openRemovedGamesCleanupModal(romId) {
    const scope = romId === undefined ? "bulk" : "rom";
    const result = await withTimeout(getPrunePreview(requestFor(scope, romId ?? null, null, 0)), PRUNE_CALLABLE_TIMEOUT_MS);
    if (!result.success)
        throw new Error(result.message ?? "Cleanup scan failed.");
    if ((result.total ?? 0) === 0)
        return false;
    if (!result.preview_id)
        throw new Error("Cleanup scan response carried no preview id.");
    beginPrunePreview(result.preview_id);
    DFL.showModal(SP_JSX.jsx(CleanupModal, { initial: result, scope: scope, romId: romId ?? null }));
    return true;
}
const RemovedGamesCleanupSection = () => {
    const [scanning, setScanning] = SP_REACT.useState(false);
    const [cancelRequestedFor, setCancelRequestedFor] = SP_REACT.useState(null);
    const [cancelStatus, setCancelStatus] = SP_REACT.useState(null);
    const [syncRunning, setSyncRunning] = SP_REACT.useState(getSyncProgress().running);
    const [pruneState, setPruneState] = SP_REACT.useState(getPruneState());
    const [resultLost, setResultLost] = SP_REACT.useState(isPruneResultLost());
    const lastRunIdRef = SP_REACT.useRef(getPruneState().runId);
    SP_REACT.useEffect(() => {
        const unsubscribeSync = onSyncProgressChange(() => setSyncRunning(getSyncProgress().running));
        const unsubscribePrune = onPruneStateChange(() => {
            const next = getPruneState();
            if (next.runId !== lastRunIdRef.current) {
                lastRunIdRef.current = next.runId;
                setCancelStatus(null);
            }
            setPruneState(next);
            setResultLost(isPruneResultLost());
        });
        return () => {
            unsubscribeSync();
            unsubscribePrune();
        };
    }, []);
    const scan = async () => {
        setScanning(true);
        try {
            if (!(await openRemovedGamesCleanupModal())) {
                showToast("No removed RomM entries were found.");
            }
        }
        catch (e) {
            logError(`Removed-game cleanup scan failed: ${e}`);
            showToast("Could not scan removed RomM games.");
        }
        finally {
            setScanning(false);
        }
    };
    const progress = pruneState.progress;
    const complete = pruneState.complete;
    const runActive = complete === null && pruneState.runId !== null;
    const cancelling = runActive && cancelRequestedFor !== null && cancelRequestedFor === pruneState.runId;
    const runLabel = progress
        ? `${progress.stage.replace(/_/g, " ")} · ${progress.current} of ${progress.total} · ${progress.name}`
        : "Cleanup starting...";
    return (SP_JSX.jsxs(DFL.PanelSection, { title: "Removed RomM Games", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", disabled: scanning || syncRunning || runActive || progress !== null, description: scanButtonDescription(syncRunning, runActive), onClick: () => detach(scan()), children: scanning ? "Scanning..." : "Clean Up Removed RomM Games" }) }), resultLost && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: RESULT_LOST_MESSAGE }) })), runActive && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: progress ? SP_JSX.jsx(CleanupProgress, { progress: progress }) : SP_JSX.jsx(DFL.Field, { label: runLabel, description: CANCEL_HINT }) }), progress?.bundle_path && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: `Recovery sealed: ${progress.bundle_path}` }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", disabled: cancelling, description: cancelStatus ?? (cancelling ? CANCELLING_HINT : undefined), onClick: () => detach((async () => {
                                const runId = pruneState.runId;
                                setCancelRequestedFor(runId);
                                const failure = await requestPruneCancel(runId);
                                setCancelStatus(failure);
                                if (failure !== null)
                                    setCancelRequestedFor(null);
                            })()), children: cancelling ? "Stopping..." : "Stop Cleanup" }) })] })), complete && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(FinishedCleanupBar, {}) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: `${complete.removed_count ?? complete.removed_rom_ids.length} removed; ${complete.problem_count ?? complete.results.filter((item) => ["partial", "failed", "skipped"].includes(item.status)).length} skipped, partial, or failed`, description: [
                                complete.message,
                                ...complete.results
                                    .filter((item) => item.status !== "removed" || (item.warnings?.length ?? 0) > 0)
                                    .flatMap((item) => [item.message, ...(item.warnings ?? []).map((warning) => `Warning: ${warning}`)]),
                            ]
                                .filter(Boolean)
                                .join(" · ") }) })] }))] }));
};

const ACTIVE_ACCENT = "#59b6ff";
const NEUTRAL_GREY = "#dcdedf";
const reportVersionListReachability = (result) => {
    if (result.server_query_failed) {
        reportServerReachable(false);
    }
    else if (result.multi_version && !result.bound_vanished) {
        reportServerReachable(true);
    }
};
const BADGE_COLORS = {
    accent: { bg: "rgba(89, 182, 255, 0.18)", fg: ACTIVE_ACCENT },
    good: { bg: "rgba(91, 163, 43, 0.22)", fg: "#7ac74f" },
    muted: { bg: "rgba(255, 255, 255, 0.10)", fg: "rgba(255, 255, 255, 0.55)" },
};
const VANISHED_HINT = "No longer available on RomM";
const REMOVE_LOCAL_DATA_LABEL = "Remove local data";
const RemoveLocalDataIcon = ({ onMenuRow, style }) => (SP_JSX.jsx(FaTrash, { size: 14, role: "img", "aria-label": REMOVE_LOCAL_DATA_LABEL, className: onMenuRow ? "romm-vanished-trash romm-vanished-trash-row" : "romm-vanished-trash", style: style }));
const AvailabilityHint = ({ text }) => (SP_JSX.jsx("span", { style: { marginLeft: "8px", fontSize: "11px", fontStyle: "italic", color: NEUTRAL_GREY }, children: text }));
const Badge = ({ text, tone }) => {
    const { bg, fg } = BADGE_COLORS[tone];
    return (SP_JSX.jsx("span", { style: {
            marginLeft: "8px",
            padding: "1px 7px",
            borderRadius: "10px",
            fontSize: "11px",
            fontWeight: 600,
            backgroundColor: bg,
            color: fg,
        }, children: text }));
};
const VersionPicker = ({ appId }) => {
    const leaseOwner = `version-picker:${appId}`;
    const [versionList, setVersionList] = SP_REACT.useState(null);
    const [switching, setSwitching] = SP_REACT.useState(false);
    const [covers, setCovers] = SP_REACT.useState({});
    const coversRequested = SP_REACT.useRef(new Set());
    const memberIdsRef = SP_REACT.useRef(new Set());
    const listRequestIdRef = SP_REACT.useRef(0);
    const loadVersionListRef = SP_REACT.useRef(null);
    SP_REACT.useEffect(() => {
        mountPruneLeaseOwner(leaseOwner);
        let cancelled = false;
        const load = async (source = "normal") => {
            const requestId = ++listRequestIdRef.current;
            const isCurrent = () => !cancelled && requestId === listRequestIdRef.current;
            try {
                const result = await getVersionList(appId);
                if (!isCurrent())
                    return;
                reportVersionListReachability(result);
                setBoundVanished(appId, result.bound_vanished);
                memberIdsRef.current = new Set((result.versions ?? []).map((v) => v.rom_id));
                setVersionList(result);
            }
            catch (e) {
                if (!isCurrent())
                    return;
                if (source === "vanished_refusal") {
                    logWarn(`VersionPicker: version-vanished list refresh failed: ${e}`);
                }
                else {
                    logError(`VersionPicker: getVersionList failed: ${e}`);
                }
            }
            finally {
                if (source === "normal" && isCurrent())
                    setSwitching(false);
            }
        };
        loadVersionListRef.current = { appId, load };
        detach(load());
        const onDataChanged = (e) => {
            const detail = e.detail;
            const switched = detail.type === "version_switched" && detail.app_id === appId;
            const pruned = detail.type === "rom_pruned" &&
                (detail.app_ids.includes(appId) || detail.rom_ids.some((romId) => memberIdsRef.current.has(romId)));
            if (switched || pruned)
                detach(load());
        };
        globalThis.addEventListener("romm_data_changed", onDataChanged);
        const onInstallChanged = (romId) => {
            if (memberIdsRef.current.has(romId))
                detach(load());
        };
        const dlComplete = addEventListener("download_complete", (evt) => onInstallChanged(evt.rom_id));
        const dlFailed = addEventListener("download_failed", (evt) => onInstallChanged(evt.rom_id));
        const onUninstalled = (e) => onInstallChanged(e.detail.rom_id);
        globalThis.addEventListener("romm_rom_uninstalled", onUninstalled);
        return () => {
            cancelled = true;
            detach(releasePruneLeasesByOwner(leaseOwner));
            if (loadVersionListRef.current?.load === load)
                loadVersionListRef.current = null;
            globalThis.removeEventListener("romm_data_changed", onDataChanged);
            removeEventListener("download_complete", dlComplete);
            removeEventListener("download_failed", dlFailed);
            globalThis.removeEventListener("romm_rom_uninstalled", onUninstalled);
        };
    }, [appId, leaseOwner]);
    SP_REACT.useEffect(() => {
        const versions = versionList?.versions;
        if (!versions)
            return;
        let cancelled = false;
        for (const v of versions) {
            if (coversRequested.current.has(v.rom_id))
                continue;
            coversRequested.current.add(v.rom_id);
            fetchCoverBase64(v.rom_id)
                .then((result) => {
                if (!cancelled && result.base64)
                    setCovers((prev) => ({ ...prev, [v.rom_id]: result.base64 }));
            })
                .catch(() => { });
        }
        return () => {
            cancelled = true;
        };
    }, [versionList]);
    const applySwitchSuccess = async (result, admission) => {
        const confirmed = await applyCommittedVersionSwitch(result, (romId, cover) => setCovers((prev) => ({ ...prev, [romId]: cover })), admission);
        if (!confirmed) {
            showToast("Switched — re-switch if launch fails");
        }
    };
    const refreshAfterVanishedRefusal = () => {
        const loader = loadVersionListRef.current;
        if (loader?.appId !== appId)
            return Promise.resolve();
        return loader.load("vanished_refusal");
    };
    const handleSwitchFailure = (result) => {
        if (result.reason === "server_unreachable")
            reportServerReachable(false);
        setSwitching(false);
        showToast("Could not switch version", { subtext: result.message });
        if (result.reason === "version_vanished")
            detach(refreshAfterVanishedRefusal());
    };
    const syncThenSwitch = async (unsyncedRomId, target, admission) => {
        const refreshStrandedSaveStatus = () => {
            detach(refreshSaveStatus$1(unsyncedRomId).catch((e) => logWarn(`VersionPicker: post-abort save-status refresh failed for rom ${unsyncedRomId}: ${e}`)));
        };
        const abort = (body) => {
            setSwitching(false);
            showToast(body);
            refreshStrandedSaveStatus();
        };
        if (!isPruneLeaseAdmissionCurrent(admission))
            return;
        try {
            const sync = await syncRomSaves(unsyncedRomId);
            if (!isPruneLeaseAdmissionCurrent(admission))
                return;
            if (!sync.success) {
                abort("Couldn't sync saves — try again");
                return;
            }
            if (sync.conflicts && sync.conflicts.length > 0) {
                abort("Resolve save conflicts first");
                return;
            }
            if (!isPruneLeaseAdmissionCurrent(admission))
                return;
            const retry = await switchVersion(appId, target.rom_id, false);
            if (retry.success) {
                await applySwitchSuccess(retry, admission);
            }
            else if (retry.reason === "unsynced_saves") {
                abort("Saves still unsynced — try again");
            }
            else {
                handleSwitchFailure(retry);
                refreshStrandedSaveStatus();
            }
        }
        catch (e) {
            if (!isPruneLeaseAdmissionCurrent(admission))
                return;
            logError(`VersionPicker: sync-then-switch failed: ${e}`);
            abort("Couldn't sync saves — try again");
        }
    };
    const resolveUnsyncedSaves = async (result, target, admission) => {
        reportServerReachable(result.server_reachable);
        const choice = await showUnsyncedSavesModal({
            versionName: result.unsynced_version_name,
            serverReachable: result.server_reachable,
        });
        if (!isPruneLeaseAdmissionCurrent(admission))
            return;
        if (choice === "cancel") {
            setSwitching(false);
            return;
        }
        if (choice === "sync_and_switch") {
            await syncThenSwitch(result.unsynced_rom_id, target, admission);
            return;
        }
        const forced = await switchVersion(appId, target.rom_id, true);
        if (forced.success) {
            await applySwitchSuccess(forced, admission);
        }
        else {
            handleSwitchFailure(forced);
        }
    };
    const handleSwitch = async (target) => {
        if (target.active || target.vanished)
            return;
        if (!target.switchable)
            return;
        setSwitching(true);
        const admission = capturePruneLeaseAdmission(leaseOwner);
        try {
            const result = await switchVersion(appId, target.rom_id, false);
            if (result.success) {
                await applySwitchSuccess(result, admission);
                return;
            }
            if (result.reason === "unsynced_saves") {
                await resolveUnsyncedSaves(result, target, admission);
                return;
            }
            handleSwitchFailure(result);
        }
        catch (e) {
            if (isPruneLeaseCancellation(e, admission)) {
                logWarn(`VersionPicker: version switch continuation was cancelled: ${e}`);
                return;
            }
            setSwitching(false);
            logError(`VersionPicker: switchVersion failed: ${e}`);
            showToast("Could not switch version");
        }
    };
    const openCleanup = (romId) => {
        detach(openRemovedGamesCleanupModal(romId)
            .then((opened) => {
            if (!opened)
                showToast("This local entry already changed.");
        })
            .catch((error) => {
            logError(`VersionPicker: cleanup preview failed for rom ${romId}: ${error}`);
            showToast("Could not prepare local cleanup.");
        }));
    };
    if (!versionList?.multi_version) {
        const bound = versionList?.bound_version;
        if (!versionList?.bound_vanished || !bound?.synced)
            return null;
        return (SP_JSX.jsxs("span", { style: { display: "inline-flex", alignItems: "center" }, children: [SP_JSX.jsx(DFL.DialogButton, { className: "romm-disc-btn", onClick: () => openCleanup(bound.rom_id), "aria-label": REMOVE_LOCAL_DATA_LABEL, title: REMOVE_LOCAL_DATA_LABEL, children: SP_JSX.jsx(RemoveLocalDataIcon, {}) }), SP_JSX.jsx(AvailabilityHint, { text: VANISHED_HINT })] }));
    }
    if (!versionList.versions || versionList.versions.length === 0)
        return null;
    const versions = versionList.versions;
    const active = versions.find((v) => v.active);
    const activeIsDefault = active?.is_default ?? false;
    const rowCover = (v) => {
        const base64 = covers[v.rom_id];
        if (base64) {
            return (SP_JSX.jsx("img", { alt: "", src: `data:image/png;base64,${base64}`, style: { width: "28px", height: "28px", borderRadius: "3px", objectFit: "cover", flexShrink: 0 } }));
        }
        return SP_JSX.jsx(FaCompactDisc, { size: 20, color: NEUTRAL_GREY, style: { flexShrink: 0 } });
    };
    const rowAvailabilityHint = (v) => {
        if (v.vanished)
            return SP_JSX.jsx(AvailabilityHint, { text: VANISHED_HINT });
        if (!v.switchable)
            return SP_JSX.jsx(AvailabilityHint, { text: "conflicting metadata match in RomM" });
        return null;
    };
    const openMenu = (e) => {
        if (switching)
            return;
        DFL.showContextMenu(SP_JSX.jsx(DFL.Menu, { label: "Version", children: versions.map((v) => {
                const removable = v.vanished && v.synced;
                return (SP_JSX.jsx(DFL.MenuItem, { disabled: !removable && (v.vanished || !v.switchable), ...(removable ? { tone: "destructive" } : {}), onClick: () => (removable ? openCleanup(v.rom_id) : detach(handleSwitch(v))), children: SP_JSX.jsxs("span", { style: {
                            display: "inline-flex",
                            alignItems: "center",
                            gap: "10px",
                            width: "100%",
                            color: v.active ? ACTIVE_ACCENT : undefined,
                            opacity: v.vanished || !v.switchable ? 0.55 : undefined,
                        }, children: [rowCover(v), SP_JSX.jsx("span", { children: v.label || v.name || String(v.rom_id) }), v.is_default ? SP_JSX.jsx(Badge, { text: "Default", tone: "accent" }) : null, v.installed ? SP_JSX.jsx(Badge, { text: "Downloaded", tone: "good" }) : null, v.switchable && !v.synced ? SP_JSX.jsx(Badge, { text: "not synced", tone: "muted" }) : null, rowAvailabilityHint(v), v.active ? SP_JSX.jsx("span", { style: { marginLeft: "6px", fontWeight: 700 }, children: "\u2713" }) : null, removable ? SP_JSX.jsx(RemoveLocalDataIcon, { onMenuRow: true, style: { marginLeft: "auto", flexShrink: 0 } }) : null] }) }, v.rom_id));
            }) }), getEventTarget(e));
    };
    return (SP_JSX.jsxs(DFL.DialogButton, { className: "romm-disc-btn", onClick: openMenu, disabled: switching, "aria-label": "Version", title: "Version", style: switching ? { opacity: 0.55 } : {}, children: [SP_JSX.jsx(FaLayerGroup, { size: 20, color: activeIsDefault ? NEUTRAL_GREY : ACTIVE_ACCENT }), switching ? (SP_JSX.jsx("span", { className: "romm-throbber", style: { width: "14px", height: "14px" } })) : (SP_JSX.jsx(FaChevronDown, { size: 10, color: "#cfd3d8" }))] }));
};

const WarningCard = ({ title, message, compact = false }) => {
    return (SP_JSX.jsxs("div", { style: {
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            padding: compact ? "24px 16px" : "40px 32px",
            gap: "14px",
            textAlign: "center",
            background: "rgba(14, 20, 27, 0.55)",
            border: "1px solid rgba(255, 170, 0, 0.35)",
            borderRadius: "6px",
            margin: compact ? "8px 4px" : "24px 2.8vw",
        }, children: [SP_JSX.jsx(FaExclamationTriangle, { style: { color: "#ffaa00", fontSize: compact ? "28px" : "42px" } }), SP_JSX.jsx("div", { style: {
                    fontSize: compact ? "15px" : "19px",
                    fontWeight: 600,
                    color: "rgba(255, 255, 255, 0.95)",
                }, children: title }), SP_JSX.jsx("div", { style: {
                    fontSize: compact ? "12px" : "14px",
                    color: "rgba(255, 255, 255, 0.75)",
                    maxWidth: compact ? "100%" : "680px",
                    lineHeight: 1.5,
                }, children: message })] }));
};

const artworkGenerations = new Map();
async function applyIcon(appId, base64, signal) {
    if (isPruneLeaseCancelled(signal))
        return false;
    const iconResult = await saveShortcutIcon(appId, base64);
    if (isPruneLeaseCancelled(signal))
        return false;
    if (iconResult.success && iconResult.icon_path) {
        SteamClient.Apps.SetShortcutIcon(appId, iconResult.icon_path);
        return true;
    }
    return false;
}
async function applyArtwork(romId, appId) {
    const leaseOwner = `artwork:${appId}`;
    mountPruneLeaseOwner(leaseOwner);
    const admission = capturePruneLeaseAdmission(leaseOwner);
    const generation = (artworkGenerations.get(appId) ?? 0) + 1;
    artworkGenerations.set(appId, generation);
    const superseded = () => artworkGenerations.get(appId) !== generation;
    const results = await Promise.all([
        getSgdbArtworkBase64(romId, 1).catch(() => ({ base64: null, no_api_key: false })),
        getSgdbArtworkBase64(romId, 2).catch(() => ({ base64: null, no_api_key: false })),
        getSgdbArtworkBase64(romId, 3).catch(() => ({ base64: null, no_api_key: false })),
        getSgdbArtworkBase64(romId, 4).catch(() => ({ base64: null, no_api_key: false })),
    ]);
    const leaseTokens = results.map((result) => ("prune_lease_token" in result ? result.prune_lease_token : undefined));
    if (results.some((r) => r.no_api_key)) {
        return withPruneLeases(leaseTokens, "Artwork apply", async () => -1, leaseOwner, admission);
    }
    return withPruneLeases(leaseTokens, "Artwork apply", async (signal) => {
        let applied = 0;
        const bail = () => {
            detach(debugLog(`applyArtwork: superseded for appId ${appId}, skipping stale writes`));
            return applied;
        };
        const customArt = [
            [results[0].base64, 1],
            [results[1].base64, 2],
            [results[2].base64, 3],
        ];
        for (const [base64, assetType] of customArt) {
            if (!base64)
                continue;
            if (isPruneLeaseCancelled(signal))
                return applied;
            if (superseded())
                return bail();
            await SteamClient.Apps.SetCustomArtworkForApp(appId, base64, "png", assetType);
            applied++;
        }
        if (results[3].base64) {
            if (isPruneLeaseCancelled(signal))
                return applied;
            if (superseded())
                return bail();
            if (await applyIcon(appId, results[3].base64, signal))
                applied++;
        }
        return applied;
    }, leaseOwner, admission);
}
async function cancelArtworkApply(appId) {
    artworkGenerations.set(appId, (artworkGenerations.get(appId) ?? 0) + 1);
    await releasePruneLeasesByOwner(`artwork:${appId}`);
}

const Tile = ({ thumbUrl, title, subtitle, onSelect, onFocus, disabled }) => (SP_JSX.jsxs(DFL.DialogButton, { onClick: onSelect, ...(onFocus !== undefined ? { onFocus } : {}), ...(disabled !== undefined ? { disabled } : {}), style: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "6px",
        padding: "8px",
        width: "100%",
        height: "auto",
        minWidth: "0",
    }, children: [thumbUrl ? (SP_JSX.jsx("img", { src: thumbUrl, alt: title, style: { width: "120px", height: "68px", objectFit: "cover", borderRadius: "4px" } })) : (SP_JSX.jsx("div", { style: {
                width: "120px",
                height: "68px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                background: "rgba(255,255,255,0.08)",
                borderRadius: "4px",
                fontSize: "11px",
                color: "rgba(255,255,255,0.5)",
            }, children: "No preview" })), SP_JSX.jsx("div", { style: { fontSize: "12px", color: "#fff", textAlign: "center", lineHeight: "1.2" }, children: title }), subtitle ? SP_JSX.jsx("div", { style: { fontSize: "11px", color: "rgba(255,255,255,0.55)" }, children: subtitle }) : null] }));
const SgdbGamePickerModalContent = ({ romId, appId, romName, candidates, onApplied, closeModal, }) => {
    const [term, setTerm] = SP_REACT.useState(romName);
    const [results, setResults] = SP_REACT.useState(candidates ?? []);
    const [searching, setSearching] = SP_REACT.useState(false);
    const [applying, setApplying] = SP_REACT.useState(false);
    const [searchError, setSearchError] = SP_REACT.useState(null);
    const runSearch = async () => {
        if (searching)
            return;
        setSearching(true);
        setSearchError(null);
        try {
            const res = await searchSgdbGames(term).catch((e) => {
                detach(debugLog(`SgdbGamePickerModal: searchSgdbGames rejected: ${e}`));
                return { success: false, games: [] };
            });
            if (res.success) {
                setResults(res.games);
                if (res.games.length === 0) {
                    setSearchError("No matches found.");
                }
            }
            else {
                setSearchError("Search failed. Check your connection and try again.");
                setResults([]);
            }
        }
        finally {
            setSearching(false);
        }
    };
    const applySelection = async (selectedId) => {
        if (applying)
            return;
        setApplying(true);
        try {
            const result = await applySgdbGameId(romId, selectedId).catch((e) => {
                detach(debugLog(`SgdbGamePickerModal: applySgdbGameId rejected: ${e}`));
                return { success: false };
            });
            if (!result.success) {
                showToast("Failed to apply artwork selection");
                return;
            }
            const applied = await applyArtwork(romId, appId).catch((e) => {
                detach(debugLog(`SgdbGamePickerModal: applyArtwork rejected: ${e}`));
                return 0;
            });
            if (applied === -1) {
                showToast("Set a SteamGridDB API key in settings first");
            }
            else if (applied > 0) {
                showToast(`Artwork refreshed (${applied}/4 images applied)`);
            }
            else {
                showToast("No artwork available for this game");
            }
            onApplied(applied);
            closeModal?.();
        }
        finally {
            setApplying(false);
        }
    };
    const onBodyButtonDown = (evt) => {
        if (evt.detail.button === DFL.GamepadButton.TRIGGER_RIGHT) {
            detach(runSearch());
        }
    };
    return (SP_JSX.jsx(DFL.ConfirmModal, { ...(closeModal !== undefined ? { closeModal } : {}), onOK: () => closeModal?.(), onCancel: () => closeModal?.(), strTitle: "Choose SteamGridDB Game", strOKButtonText: "Close", bAlertDialog: true, children: SP_JSX.jsxs(DFL.Focusable, { "flow-children": "column", onButtonDown: onBodyButtonDown, onOKActionDescription: "Select", actionDescriptionMap: { [DFL.GamepadButton.TRIGGER_RIGHT]: "Search" }, style: { display: "flex", flexDirection: "column", gap: "12px", width: "100%" }, children: [SP_JSX.jsx("div", { style: { fontSize: "13px", color: "rgba(255,255,255,0.6)" }, children: romName }), SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255,255,255,0.5)" }, children: "No SteamGridDB match was found automatically \u2014 search by name and pick the right game." }), SP_JSX.jsxs(DFL.Focusable, { "flow-children": "row", style: { display: "flex", gap: "8px", alignItems: "center" }, children: [SP_JSX.jsx("div", { style: { flex: 1 }, children: SP_JSX.jsx(DFL.TextField, { focusOnMount: true, label: "Search SteamGridDB", value: term, onChange: (e) => setTerm(e.target.value), onKeyDown: (e) => {
                                    if (e.key === "Enter" && !searching)
                                        detach(runSearch());
                                }, onFocus: scrollToTop }) }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => {
                                detach(runSearch());
                            }, onFocus: scrollToTop, disabled: searching, style: { width: "120px", height: "40px" }, children: "Search" })] }), searching ? (SP_JSX.jsx("div", { style: { display: "flex", justifyContent: "center", padding: "16px" }, children: SP_JSX.jsx("div", { style: { width: "32px", height: "32px" }, children: SP_JSX.jsx(DFL.Spinner, {}) }) })) : null, searchError ? SP_JSX.jsx("div", { style: { fontSize: "12px", color: "#ff8800" }, children: searchError }) : null, results.length > 0 ? (SP_JSX.jsx("div", { style: { fontSize: "11px", color: "rgba(255,255,255,0.5)" }, children: "Showing the top 6 matches \u2014 refine your search if the right game isn't here." })) : null, results.length > 0 ? (SP_JSX.jsx(DFL.Focusable, { style: { display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "12px" }, "flow-children": "right", children: results.map((game) => (SP_JSX.jsx(Tile, { thumbUrl: game.thumb_url, title: game.name, subtitle: game.release_year == null ? undefined : String(game.release_year), onSelect: () => {
                            detach(applySelection(game.id));
                        }, onFocus: scrollFocusedToCenter, disabled: applying }, game.id))) })) : null] }) }));
};

function reasonCopy(reason) {
    switch (reason) {
        case "inject":
            return "needs setup files (launch via ES-DE once)";
        case "not_installed":
            return "emulator not installed";
        case "external_launcher":
            return "external emulator — not launchable from Steam yet";
        case "shortcut_script":
            return "script/shortcut form";
        default:
            return "not launchable from Steam";
    }
}
function emulatorEntryLabel(e, isActive, isPlatformCore) {
    const defaultMark = e.is_default ? " (default)" : "";
    const systemMark = isPlatformCore ? " (system)" : "";
    const activeMark = isActive ? " ✓" : "";
    return `${e.label}${defaultMark}${systemMark}${activeMark}`;
}
function buildEmulatorMenu(config) {
    const { emulators, emulatorDataAvailable, activeLabel, platformCoreLabel, followSystem, onPick } = config;
    if (!emulatorDataAvailable) {
        return (SP_JSX.jsx(DFL.Menu, { label: "Emulator", children: SP_JSX.jsx(DFL.MenuItem, { disabled: true, children: "Emulator list unavailable \u2014 RetroDECK installation not found" }, "unavailable") }));
    }
    const defaultLabel = emulators.find((e) => e.is_default)?.label ?? null;
    const activeIsDefault = !activeLabel || activeLabel === defaultLabel;
    const children = [
        SP_JSX.jsx(DFL.MenuItem, { disabled: true, children: "Switching cores may affect save compatibility" }, "compat"),
        SP_JSX.jsx(DFL.MenuSeparator, {}, "compat-sep"),
    ];
    if (followSystem) {
        const fallbackLabel = platformCoreLabel ?? defaultLabel ?? null;
        const fallbackSuffix = fallbackLabel ? ` (${fallbackLabel})` : "";
        const followsSystemMark = followSystem.hasGameOverride ? "" : " ✓";
        children.push(SP_JSX.jsx(DFL.MenuItem, { onClick: followSystem.onFollowSystem, children: `Use System Override${fallbackSuffix}${followsSystemMark}` }, "follow-system"), SP_JSX.jsx(DFL.MenuSeparator, {}, "follow-sep"));
    }
    for (const e of emulators) {
        const key = `emu-${e.label}`;
        if (!e.bakeable) {
            children.push(SP_JSX.jsx(DFL.MenuItem, { disabled: true, children: `${e.label} — ${reasonCopy(e.reason)}` }, key));
            continue;
        }
        const isActive = activeIsDefault ? e.is_default : activeLabel === e.label;
        const isPlatformCore = platformCoreLabel !== null && e.label === platformCoreLabel;
        children.push(SP_JSX.jsx(DFL.MenuItem, { onClick: () => onPick(e.label), children: emulatorEntryLabel(e, isActive, isPlatformCore) }, key));
    }
    return SP_JSX.jsx(DFL.Menu, { label: "Emulator Core", children: children });
}

const BIOS_MISSING_RED = "#d94126";
function biosColorForLevel(level) {
    switch (level) {
        case "ok":
            return "#5ba32b";
        case "partial":
            return "#d4a72c";
        case "missing":
            return BIOS_MISSING_RED;
        case "unknown":
            return "#8f98a0";
        default:
            return "#8f98a0";
    }
}

function resolveSaveSyncLabel(display) {
    if (display.label !== null)
        return display.label;
    if (display.last_sync_check_at) {
        return formatTimeAgo(display.last_sync_check_at) ?? "Not synced";
    }
    return "Not synced";
}
function applySaveSyncDisplay(display, saveStatus) {
    if (display) {
        return { status: display.status, label: resolveSaveSyncLabel(display) };
    }
    if (hasAnySaveConflict(saveStatus))
        return { status: "conflict", label: "Conflict" };
    return { status: "none", label: "No saves" };
}
function extractBiosInfo(answer) {
    if (answer.bios_status_unknown) {
        if (answer.bios_level !== "unknown")
            return null;
        return { biosNeeded: false, biosLabel: "", biosRequiredMissing: false };
    }
    if (!answer.bios_status) {
        return { biosNeeded: false, biosLabel: "", biosRequiredMissing: false };
    }
    const requiredCount = answer.bios_status.required_count ?? 0;
    const requiredDownloaded = answer.bios_status.required_downloaded ?? 0;
    const requiredJudged = requiredCount - (answer.bios_status.required_withheld ?? 0);
    const systemImageAbsent = answer.bios_status.system_image === "absent";
    return {
        biosNeeded: true,
        biosLabel: answer.bios_label ?? "",
        biosRequiredMissing: systemImageAbsent || (requiredJudged > 0 && requiredDownloaded < requiredJudged),
    };
}
function extractCoreInfo(coreInfo) {
    const activeCoreLabel = coreInfo.active_core_label ?? null;
    const emulators = coreInfo.emulators;
    const defaultEmulator = emulators.find((e) => e.is_default);
    const activeCoreIsDefault = !activeCoreLabel || activeCoreLabel === defaultEmulator?.label;
    return {
        activeCoreLabel,
        activeCoreIsDefault,
        emulators,
        emulatorDataAvailable: coreInfo.emulator_data_available,
        platformCoreLabel: coreInfo.platform_core_label ?? null,
        hasGameOverride: coreInfo.has_game_override,
    };
}
function timeoutMs(ms) {
    return new Promise((_, reject) => setTimeout(() => reject(new Error("timeout")), ms));
}

function shareInFlight(read) {
    const inFlight = new Map();
    return (arg) => {
        const open = inFlight.get(arg);
        if (open)
            return open;
        const request = read(arg);
        inFlight.set(arg, request);
        const release = () => {
            if (inFlight.get(arg) === request)
                inFlight.delete(arg);
        };
        request.then(release, release);
        return request;
    };
}
const getRomMetadataShared = shareInFlight(getRomMetadata);
const getPlatformCoreInfoShared = shareInFlight(getPlatformCoreInfo);
const getBiosStatusShared = shareInFlight(getBiosStatus);

function refreshBiosInBackground(romId, cancelled, setter) {
    getBiosStatusShared(romId)
        .then((result) => {
        if (cancelled())
            return;
        const biosInfo = extractBiosInfo(result);
        if (!biosInfo)
            return;
        setter((prev) => ({ ...prev, ...biosInfo }));
    })
        .catch((e) => debugLog(`Background BIOS status fetch error: ${e}`));
}
function refreshCoreInfoInBackground(romId, cancelled, setter) {
    getPlatformCoreInfoShared(romId)
        .then((coreInfo) => {
        if (!cancelled()) {
            setter((prev) => ({
                ...prev,
                ...extractCoreInfo(coreInfo),
            }));
        }
    })
        .catch((e) => debugLog(`Background core info fetch error: ${e}`));
}
function refreshAchievementsInBackground(romId, cancelled, setter) {
    getAchievementProgress(romId)
        .then((result) => {
        if (!cancelled() && result.success) {
            setter((prev) => ({
                ...prev,
                achievementEarned: result.earned,
                achievementTotal: result.total,
            }));
        }
    })
        .catch((e) => debugLog(`Background achievement progress fetch error: ${e}`));
}

const DEFAULT_STATE = {
    romId: null,
    romName: "",
    platformSlug: "",
    installed: false,
    fsSizeBytes: null,
    saveSyncEnabled: false,
    saveStatus: null,
    saveSyncStatus: null,
    saveSyncLabel: "",
    savefilesInContentDir: false,
    activeSlot: "default",
    raId: null,
    achievementEarned: 0,
    achievementTotal: 0,
    biosNeeded: false,
    biosLabel: "",
    biosRequiredMissing: false,
    activeCoreLabel: null,
    activeCoreIsDefault: true,
    emulators: [],
    emulatorDataAvailable: true,
    platformCoreLabel: null,
    hasGameOverride: false,
};
const UNKNOWN_BIOS_STATUS = {
    bios_status: null,
    bios_level: null,
    bios_label: null,
    bios_status_unknown: true,
};
const _entries = new Map();
function getGameDetail(appId) {
    return _entries.get(appId)?.state ?? DEFAULT_STATE;
}
function subscribeGameDetail(appId, cb) {
    const entry = openEntry(appId);
    entry.listeners.add(cb);
    return () => {
        entry.listeners.delete(cb);
        if (entry.listeners.size === 0 && _entries.get(appId) === entry)
            closeEntry(appId, entry);
    };
}
function useGameDetail(appId) {
    const subscribe = SP_REACT.useCallback((onChange) => subscribeGameDetail(appId, onChange), [appId]);
    const snapshot = SP_REACT.useCallback(() => getGameDetail(appId), [appId]);
    return SP_REACT.useSyncExternalStore(subscribe, snapshot);
}
function openEntry(appId) {
    const existing = _entries.get(appId);
    if (existing)
        return existing;
    const entry = {
        state: DEFAULT_STATE,
        listeners: new Set(),
        generation: 0,
        loadSeq: 0,
        loadFailed: false,
        timedRetryUsed: false,
        saveStatusInFlight: null,
        detachListeners: () => { },
    };
    _entries.set(appId, entry);
    entry.detachListeners = attachListeners(appId, entry);
    detach(loadDetail(appId, entry));
    return entry;
}
function closeEntry(appId, entry) {
    entry.generation++;
    entry.saveStatusInFlight = null;
    entry.detachListeners();
    _entries.delete(appId);
}
function writerFor(entry, generation) {
    return (update) => {
        if (entry.generation !== generation)
            return;
        entry.state = typeof update === "function" ? update(entry.state) : update;
        entry.listeners.forEach((listener) => listener(entry.state));
    };
}
function writerForRom(entry, generation, romId) {
    const write = writerFor(entry, generation);
    return (update) => {
        if (entry.state.romId !== romId)
            return;
        write(update);
    };
}
async function loadDetail(appId, entry) {
    const generation = entry.generation;
    const loadSeq = ++entry.loadSeq;
    entry.loadFailed = false;
    const cancelled = () => entry.generation !== generation || entry.loadSeq !== loadSeq;
    const write = writerFor(entry, generation);
    try {
        const cached = await getCachedGameDetail(appId);
        const romId = cached.rom_id;
        if (cancelled() || !cached.found || !romId)
            return;
        let saveSyncStatus = null;
        let saveSyncLabel = "";
        if (cached.save_sync_enabled && cached.save_sync_display) {
            saveSyncStatus = cached.save_sync_display.status;
            saveSyncLabel = resolveSaveSyncLabel(cached.save_sync_display);
        }
        write((prev) => ({
            ...prev,
            romId,
            romName: cached.rom_name || "",
            platformSlug: cached.platform_slug || "",
            installed: cached.installed ?? false,
            fsSizeBytes: cached.fs_size_bytes ?? null,
            saveSyncEnabled: cached.save_sync_enabled ?? false,
            saveSyncStatus,
            saveSyncLabel,
            raId: cached.ra_id ?? null,
            achievementEarned: cached.achievement_summary?.earned ?? prev.achievementEarned,
            achievementTotal: cached.achievement_summary?.total ?? prev.achievementTotal,
        }));
        const writeForRom = writerForRom(entry, generation, romId);
        if (cached.save_sync_enabled)
            detach(refreshSaveStatus(appId));
        const staleFields = cached.stale_fields ?? [];
        if (staleFields.includes("metadata")) {
            getRomMetadataShared(romId).catch((e) => debugLog(`Background metadata fetch error: ${e}`));
        }
        if (cached.ra_id && staleFields.includes("achievements")) {
            refreshAchievementsInBackground(romId, cancelled, writeForRom);
        }
        const cachedBios = extractBiosInfo(cached);
        if (cachedBios)
            write((prev) => ({ ...prev, ...cachedBios }));
        if (staleFields.includes("bios")) {
            refreshBiosInBackground(romId, cancelled, writeForRom);
        }
        refreshCoreInfoInBackground(romId, cancelled, writeForRom);
    }
    catch (e) {
        logError(`gameDetailStore: load error: ${e}`);
        if (!cancelled()) {
            entry.loadFailed = true;
            scheduleFailedLoadRetry(appId, entry);
        }
    }
}
function refreshSaveStatus(appId) {
    const entry = _entries.get(appId);
    if (!entry)
        return Promise.resolve(null);
    const romId = entry.state.romId;
    if (!romId)
        return Promise.resolve(null);
    const inFlight = entry.saveStatusInFlight;
    if (inFlight?.romId === romId)
        return inFlight.promise;
    const request = readSaveStatus(entry, romId, entry.generation);
    entry.saveStatusInFlight = { romId, promise: request };
    const release = () => {
        if (entry.saveStatusInFlight?.promise === request)
            entry.saveStatusInFlight = null;
    };
    request.then(release, release);
    return request;
}
async function readSaveStatus(entry, romId, generation) {
    const result = await getSaveStatus(romId);
    if (isCallableFailure(result)) {
        detach(debugLog(`gameDetailStore: save status refused: ${result.message}`));
        return null;
    }
    applySaveStatus(entry, generation, result);
    return result;
}
function applySaveStatus(entry, generation, status) {
    if (status.rom_id !== entry.state.romId)
        return;
    const { status: saveSyncStatus, label: saveSyncLabel } = applySaveSyncDisplay(status.save_sync_display, status);
    writerFor(entry, generation)((prev) => ({
        ...prev,
        saveStatus: status,
        saveSyncStatus,
        saveSyncLabel,
        savefilesInContentDir: status.savefiles_in_content_dir === true,
        activeSlot: "active_slot" in status ? (status.active_slot ?? null) : prev.activeSlot,
    }));
}
function noteSaveSyncDisplay(appId, romId, display) {
    const entry = _entries.get(appId);
    if (!entry)
        return;
    writerForRom(entry, entry.generation, romId)((prev) => ({
        ...prev,
        saveSyncStatus: display.status,
        saveSyncLabel: resolveSaveSyncLabel(display),
    }));
}
async function refreshBiosStatus(appId) {
    const entry = _entries.get(appId);
    const romId = entry?.state.romId;
    if (!entry || !romId)
        return;
    const generation = entry.generation;
    const refreshed = await getBiosStatus(romId).catch(() => UNKNOWN_BIOS_STATUS);
    const biosInfo = extractBiosInfo(refreshed);
    if (!biosInfo?.biosNeeded)
        return;
    writerForRom(entry, generation, romId)((prev) => ({ ...prev, ...biosInfo }));
}
async function refreshCoreAndBios(appId) {
    const entry = _entries.get(appId);
    const romId = entry?.state.romId;
    if (!entry || !romId)
        return;
    const generation = entry.generation;
    const [coreInfo, refreshed] = await Promise.all([
        getPlatformCoreInfo(romId),
        getBiosStatus(romId).catch(() => UNKNOWN_BIOS_STATUS),
    ]);
    const biosInfo = extractBiosInfo(refreshed);
    writerForRom(entry, generation, romId)((prev) => ({
        ...prev,
        ...extractCoreInfo(coreInfo),
        ...biosInfo,
    }));
    invalidateCachedGameDetail(appId);
}
async function reloadDetail(appId, entry) {
    invalidateCachedGameDetail(appId);
    await loadDetail(appId, entry);
}
async function handleSaveSyncSettingsChange$1(appId, entry, detail) {
    if (!detail.save_sync_enabled) {
        writerFor(entry, entry.generation)((prev) => ({
            ...prev,
            saveSyncEnabled: false,
            saveSyncStatus: null,
            saveSyncLabel: "",
        }));
        return;
    }
    writerFor(entry, entry.generation)((prev) => ({ ...prev, saveSyncEnabled: true }));
    await refreshSaveStatus(appId).catch(() => null);
}
async function handleSaveSyncChange$1(appId, entry, detail) {
    const romId = entry.state.romId;
    if (!romId)
        return;
    if (detail.rom_id && detail.rom_id !== romId)
        return;
    if (detail.save_status) {
        applySaveStatus(entry, entry.generation, detail.save_status);
        return;
    }
    await refreshSaveStatus(appId).catch(() => null);
}
async function handleCoreChange$1(entry) {
    const romId = entry.state.romId;
    if (!romId)
        return;
    const generation = entry.generation;
    const [coreInfo, biosResult] = await Promise.all([
        getPlatformCoreInfo(romId),
        getBiosStatus(romId).catch(() => UNKNOWN_BIOS_STATUS),
    ]);
    const biosInfo = extractBiosInfo(biosResult);
    writerForRom(entry, generation, romId)((prev) => ({
        ...prev,
        ...extractCoreInfo(coreInfo),
        ...biosInfo,
    }));
}
const FAILED_LOAD_RETRY_MS = 5000;
function scheduleFailedLoadRetry(appId, entry) {
    if (entry.timedRetryUsed)
        return;
    entry.timedRetryUsed = true;
    const generation = entry.generation;
    setTimeout(() => {
        if (entry.generation !== generation || !entry.loadFailed)
            return;
        detach(reloadDetail(appId, entry));
    }, FAILED_LOAD_RETRY_MS);
}
function reloadTriggeredBy(entry, eventRomId) {
    if (entry.state.romId !== null)
        return eventRomId === entry.state.romId;
    return entry.loadFailed;
}
function attachListeners(appId, entry) {
    const onDataChanged = (e) => {
        detach((async () => {
            try {
                const detail = e.detail;
                switch (detail?.type) {
                    case "save_sync_settings":
                        await handleSaveSyncSettingsChange$1(appId, entry, detail);
                        break;
                    case "core_changed":
                        await handleCoreChange$1(entry);
                        break;
                    case "save_sync":
                        await handleSaveSyncChange$1(appId, entry, detail);
                        break;
                    case "version_switched":
                        if (detail.app_id === appId)
                            await loadDetail(appId, entry);
                        break;
                    case "rom_adopted":
                        if (reloadTriggeredBy(entry, detail.rom_id))
                            await reloadDetail(appId, entry);
                        break;
                }
            }
            catch (err) {
                detach(debugLog(`gameDetailStore: onDataChanged error: ${err}`));
            }
        })());
    };
    globalThis.addEventListener("romm_data_changed", onDataChanged);
    const onDownloadComplete = addEventListener("download_complete", (evt) => {
        if (!reloadTriggeredBy(entry, evt.rom_id))
            return;
        detach(reloadDetail(appId, entry));
    });
    const onUninstalled = (e) => {
        const romId = e.detail?.rom_id;
        if (!reloadTriggeredBy(entry, romId))
            return;
        detach(reloadDetail(appId, entry));
    };
    globalThis.addEventListener("romm_rom_uninstalled", onUninstalled);
    return () => {
        globalThis.removeEventListener("romm_data_changed", onDataChanged);
        removeEventListener("download_complete", onDownloadComplete);
        globalThis.removeEventListener("romm_rom_uninstalled", onUninstalled);
    };
}

const CONNECTION_HEARTBEAT_INTERVAL_MS = 30000;
let timer = null;
let mountedPages = 0;
async function probeOnce() {
    try {
        const r = await probeReachability();
        reportServerReachable(r.online === true);
    }
    catch (e) {
        detach(debugLog(`connectionHeartbeat: probe failed (no verdict): ${e}`));
    }
}
function registerConnectionHeartbeat() {
    mountedPages += 1;
    timer ?? (timer = setInterval(() => detach(probeOnce()), CONNECTION_HEARTBEAT_INTERVAL_MS));
    return () => {
        mountedPages -= 1;
        if (mountedPages <= 0) {
            mountedPages = 0;
            if (timer !== null) {
                clearInterval(timer);
                timer = null;
            }
        }
    };
}

let _state$3 = { pending: false, legacyDataPresent: false, dismissed: false };
let _listeners$2 = [];
function setLegacyInstallState(state) {
    _state$3 = state;
    _listeners$2.forEach((fn) => fn());
}
function getLegacyInstallState() {
    return _state$3;
}
function onLegacyInstallChange(fn) {
    _listeners$2.push(fn);
    return () => {
        _listeners$2 = _listeners$2.filter((l) => l !== fn);
    };
}
function useLegacyInstallState() {
    return SP_REACT.useSyncExternalStore(onLegacyInstallChange, getLegacyInstallState);
}
async function fetchLegacyInstallState() {
    const notice = await getLegacyInstallNotice();
    const next = {
        pending: notice.pending,
        legacyDataPresent: notice.legacy_data_present,
        dismissed: notice.dismissed,
    };
    setLegacyInstallState(next);
    return next;
}
async function dismissLegacyInstall() {
    await dismissLegacyInstallNotice();
    setLegacyInstallState({ ..._state$3, dismissed: true });
}

let _state$2 = { relocated: false };
let _listeners$1 = [];
function setLauncherRelocated(relocated) {
    _state$2 = { relocated };
    _listeners$1.forEach((fn) => fn());
}
function getLauncherState() {
    return _state$2;
}
function onLauncherChange(fn) {
    _listeners$1.push(fn);
    return () => {
        _listeners$1 = _listeners$1.filter((l) => l !== fn);
    };
}
function useLauncherRelocated() {
    return SP_REACT.useSyncExternalStore(onLauncherChange, getLauncherState).relocated;
}

const LEGACY_INSTALL_TITLE = '"RomM Sync" is still installed, and your games need it.';
const LEGACY_REMOVABLE_TITLE = '"RomM Sync" can be removed now.';
function legacyInstallStatement(relocated, dataStranded) {
    if (relocated) {
        return {
            title: LEGACY_REMOVABLE_TITLE,
            body: "Your games no longer launch through it — Arcoon Deck keeps its own copy of the file they need, outside any " +
                "plugin folder. Nothing here depends on the older install any more, so you can remove it wherever Decky " +
                "lists your installed plugins. Keeping it is fine too; it costs disk space and nothing else.",
            dismissible: true,
        };
    }
    const launcher = "Every Steam shortcut launches through a file in that older plugin's folder, so removing it from Decky stops " +
        "your games from starting. Leave it in place until Arcoon Deck has moved them onto its own copy of that file — it " +
        "tries every time it starts up, which is when your device does.";
    return {
        title: LEGACY_INSTALL_TITLE,
        body: dataStranded
            ? `${launcher} Your library and settings are still in that older install too — this version starts empty ` +
                "until the move happens."
            : launcher,
        dismissible: false,
    };
}
const LegacyInstallBanner = ({ dataStranded, relocated, onDismiss }) => {
    const statement = legacyInstallStatement(relocated, dataStranded);
    return (SP_JSX.jsxs(DFL.PanelSection, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs("div", { style: {
                        padding: "8px 12px",
                        backgroundColor: "rgba(212, 167, 44, 0.15)",
                        borderLeft: "3px solid #d4a72c",
                        borderRadius: "4px",
                    }, children: [SP_JSX.jsxs("div", { style: {
                                fontSize: "13px",
                                fontWeight: "bold",
                                color: "#d4a72c",
                                marginBottom: "6px",
                            }, children: ["⚠️", " ", statement.title] }), SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.85)", lineHeight: 1.5 }, children: statement.body })] }) }), statement.dismissible && onDismiss ? (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: onDismiss, children: "Dismiss" }) })) : null] }));
};
const LegacyInstallNotice = () => {
    const legacyInstall = useLegacyInstallState();
    const relocated = useLauncherRelocated();
    const stats = useSyncStats();
    if (!legacyInstall.pending)
        return null;
    if (relocated && legacyInstall.dismissed)
        return null;
    return (SP_JSX.jsx(LegacyInstallBanner, { dataStranded: legacyInstall.legacyDataPresent && stats?.roms === 0, relocated: relocated, onDismiss: () => {
            dismissLegacyInstall().catch((e) => logError(`Failed to dismiss the legacy-install notice: ${e}`));
        } }));
};

function useVersionError() {
    const [err, setErr] = SP_REACT.useState(getVersionError());
    SP_REACT.useEffect(() => onVersionErrorChange(setErr), []);
    return err;
}
const VersionErrorCard = ({ message, compact = false }) => (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(WarningCard, { title: "RomM Server Update Required", message: message, compact: compact }), SP_JSX.jsx(LegacyInstallNotice, {})] }));

const artworkApplied = new Map();
const CONNECTION_CHECK_DEADLINE_MS = 5000;
let connectionCheckSeq = 0;
let lastSettledCheckId = 0;
function resolveLastPlayed(restoredIso, steamUnixSeconds) {
    if (restoredIso) {
        const ms = Date.parse(restoredIso);
        if (!Number.isNaN(ms))
            return formatLastPlayed(Math.floor(ms / 1000));
    }
    return formatLastPlayed(steamUnixSeconds);
}
async function readAndBroadcastSaveStatus(appId, isCancelled) {
    try {
        const saveStatus = await refreshSaveStatus(appId);
        if (isCancelled() || saveStatus?.rom_id !== getGameDetail(appId).romId)
            return;
        globalThis.dispatchEvent(new CustomEvent("romm_data_changed", {
            detail: {
                type: "save_sync",
                rom_id: saveStatus.rom_id,
                save_status: saveStatus,
                has_conflict: hasAnySaveConflict(saveStatus),
            },
        }));
    }
    catch (e) {
        detach(debugLog(`RomMPlaySection: background save check error: ${e}`));
    }
}
const RomMPlaySection = ({ appId }) => {
    const versionError = useVersionError();
    const migration = useMigrationStatus();
    const overview = appStore.GetAppOverviewByAppID(appId);
    const initialLastPlayed = formatLastPlayed(overview?.rt_last_time_played ?? 0);
    const initialPlaytime = formatPlaytime(overview?.minutes_playtime_forever ?? 0);
    const detail = useGameDetail(appId);
    const [playtimeInfo, setPlaytimeInfo] = SP_REACT.useState({
        lastPlayed: initialLastPlayed,
        restoredLastPlayed: null,
        playtime: initialPlaytime,
    });
    const connectionState = useRommConnectionState();
    const [actionPending, setActionPending] = SP_REACT.useState(null);
    SP_REACT.useEffect(() => registerConnectionHeartbeat(), []);
    SP_REACT.useEffect(() => {
        mountPruneLeaseOwner(`game-detail:${appId}`);
        return () => {
            detach(cancelArtworkApply(appId));
            detach(releasePruneLeasesByOwner(`game-detail:${appId}`));
        };
    }, [appId]);
    SP_REACT.useEffect(() => {
        const romId = detail.romId;
        if (!romId || artworkApplied.get(appId) === romId)
            return;
        applyArtwork(romId, appId)
            .then(() => {
            artworkApplied.set(appId, romId);
        })
            .catch((e) => debugLog(`Auto-artwork error: ${e}`));
    }, [appId, detail.romId]);
    SP_REACT.useEffect(() => {
        const checkId = ++connectionCheckSeq;
        let cancelled = false;
        let settled = false;
        const superseded = () => cancelled || checkId < lastSettledCheckId;
        const settleWith = (next, reason) => {
            lastSettledCheckId = checkId;
            setRommConnectionState(next, reason);
        };
        const fastOfflineProbe = async () => {
            const offline = await probeReachability()
                .then((r) => r.online === false)
                .catch((e) => {
                detach(debugLog(`RomMPlaySection: fast reachability probe failed (no signal — deferring to testConnection): ${e}`));
                return false;
            });
            if (superseded() || settled || !offline)
                return;
            settleWith("offline", "fast probe");
        };
        const applyVerdict = (result) => {
            if (superseded())
                return;
            settled = true;
            if (result.reason === "version_error") {
                setVersionError(result.message);
                settleWith("offline", "version error");
                return;
            }
            settleWith(result.success ? "connected" : "offline", "authoritative verdict");
        };
        const runVerdict = async () => {
            let result;
            try {
                result = await testConnection();
            }
            catch (e) {
                if (superseded())
                    return;
                settled = true;
                detach(debugLog(`RomMPlaySection(${appId}): connection check failed: ${e}`));
                settleWith("offline", "check failed");
                return;
            }
            applyVerdict(result);
        };
        const check = async () => {
            setRommConnectionState("checking", "connection check started");
            detach(fastOfflineProbe());
            const verdict = runVerdict();
            await Promise.race([verdict, timeoutMs(CONNECTION_CHECK_DEADLINE_MS)]).catch(() => {
                if (superseded() || settled)
                    return;
                detach(debugLog(`RomMPlaySection(${appId}): connection check unanswered after ${CONNECTION_CHECK_DEADLINE_MS}ms — holding "checking" until the verdict lands`));
            });
        };
        detach(check());
        return () => {
            cancelled = true;
        };
    }, [appId]);
    SP_REACT.useEffect(() => {
        const romId = detail.romId;
        if (!romId || !detail.saveSyncEnabled)
            return;
        let cancelled = false;
        detach(readAndBroadcastSaveStatus(appId, () => cancelled));
        return () => {
            cancelled = true;
        };
    }, [appId, detail.romId, detail.saveSyncEnabled]);
    SP_REACT.useEffect(() => {
        let cancelled = false;
        const unsubscribe = onRommConnectionChange((next) => {
            if (next !== "connected")
                return;
            const { romId, saveSyncEnabled, saveStatus } = getGameDetail(appId);
            if (!romId || !saveSyncEnabled || !saveStatus?.server_query_failed)
                return;
            detach(readAndBroadcastSaveStatus(appId, () => cancelled));
        });
        return () => {
            cancelled = true;
            unsubscribe();
        };
    }, [appId]);
    SP_REACT.useEffect(() => {
        const romId = detail.romId;
        if (!romId)
            return;
        let cancelled = false;
        async function doReconcilePlaytime(rid, isCancelled) {
            try {
                const result = await reconcilePlaytime(rid);
                if (isCancelled())
                    return;
                if ("success" in result) {
                    detach(debugLog(`RomMPlaySection: playtime reconcile deferred: ${result.message}`));
                    return;
                }
                if (!result.server_query_failed) {
                    const steamSecs = appStore.GetAppOverviewByAppID(appId)?.rt_last_time_played ?? 0;
                    setPlaytimeInfo((prev) => ({
                        ...prev,
                        restoredLastPlayed: result.last_played,
                        lastPlayed: resolveLastPlayed(result.last_played, steamSecs),
                    }));
                }
                updatePlaytimeDisplay(appId, result.total_seconds, false);
            }
            catch (e) {
                detach(debugLog(`RomMPlaySection: playtime reconcile error: ${e}`));
            }
        }
        detach(doReconcilePlaytime(romId, () => cancelled));
        return () => {
            cancelled = true;
        };
    }, [detail.romId, appId]);
    SP_REACT.useEffect(() => {
        const onPlaytimeChanged = (e) => {
            const payload = e.detail;
            if (payload?.appId !== appId)
                return;
            const ov = appStore.GetAppOverviewByAppID(appId);
            if (!ov)
                return;
            setPlaytimeInfo((prev) => ({
                ...prev,
                playtime: formatPlaytime(ov.minutes_playtime_forever ?? 0),
                lastPlayed: resolveLastPlayed(prev.restoredLastPlayed, ov.rt_last_time_played ?? 0),
            }));
        };
        globalThis.addEventListener("romm_playtime_changed", onPlaytimeChanged);
        return () => {
            globalThis.removeEventListener("romm_playtime_changed", onPlaytimeChanged);
        };
    }, [appId]);
    const infoItem = (key, header, value, extraClass) => (SP_JSX.jsxs("div", { className: `romm-info-item ${""}`.trim(), children: [SP_JSX.jsx("div", { className: "romm-info-header", children: header }), SP_JSX.jsx("div", { className: "romm-info-value", children: value })] }, key));
    const handleRefreshArtwork = async () => {
        if (actionPending)
            return;
        if (!detail.romId) {
            showToast("ROM info not loaded yet");
            return;
        }
        const romId = detail.romId;
        setActionPending("artwork");
        const admission = capturePruneLeaseAdmission(`game-detail:${appId}`);
        try {
            const coverResult = await refreshCoverArtwork(romId).catch((e) => {
                detach(debugLog(`refreshCoverArtwork rejected: ${e}`));
                return { success: false, reason: "exception", message: String(e) };
            });
            if (coverResult.success) {
                globalThis.dispatchEvent(new CustomEvent("romm_data_changed", {
                    detail: { type: "cover_refreshed", rom_id: romId },
                }));
            }
            else {
                detach(debugLog(`refreshCoverArtwork failed: ${coverResult.reason} — ${coverResult.message}`));
            }
            const resolution = await getSgdbResolution(romId).catch((e) => {
                detach(debugLog(`getSgdbResolution rejected: ${e}`));
                return null;
            });
            if (!resolution) {
                showToast("Failed to refresh artwork");
                return;
            }
            switch (resolution.decision) {
                case "no_api_key":
                    showToast("Set a SteamGridDB API key in settings first");
                    break;
                case "resolved": {
                    const applied = await applyArtwork(romId, appId);
                    if (applied === -1) {
                        showToast("Set a SteamGridDB API key in settings first");
                    }
                    else if (applied > 0) {
                        showToast(`Artwork refreshed (${applied}/4 images applied)`);
                    }
                    else {
                        showToast("No artwork available for this game");
                    }
                    break;
                }
                case "needs_pick":
                    DFL.showModal(SP_JSX.jsx(SgdbGamePickerModalContent, { romId: romId, appId: appId, romName: detail.romName, candidates: resolution.candidates, onApplied: () => { } }));
                    break;
            }
        }
        catch (e) {
            if (isPruneLeaseCancellation(e, admission)) {
                detach(debugLog(`handleRefreshArtwork: continuation was cancelled: ${e}`));
                return;
            }
            showToast("Failed to refresh artwork");
        }
        finally {
            setActionPending(null);
        }
    };
    const handleRefreshMetadata = async () => {
        if (actionPending || !detail.romId)
            return;
        setActionPending("metadata");
        try {
            await getRomMetadata(detail.romId);
            showToast("Metadata refreshed");
            globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "metadata", rom_id: detail.romId } }));
        }
        catch {
            showToast("Failed to refresh metadata");
        }
        finally {
            setActionPending(null);
        }
    };
    const handleSyncSaves = async () => {
        if (actionPending || !detail.romId)
            return;
        const romId = detail.romId;
        setActionPending("savesync");
        try {
            const result = await syncRomSaves(romId);
            if (result.success) {
                const directionalBody = saveSyncToastBody(result.uploaded, result.downloaded);
                const c = result.conflicts?.length ?? 0;
                if (directionalBody) {
                    showToast(directionalBody);
                }
                else if (c === 0) {
                    showToast("Saves already up to date");
                }
                if (c > 0) {
                    showToast(`${c} conflict(s) need resolution`);
                }
                globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "save_sync", rom_id: romId } }));
                noteSaveSyncDisplay(appId, romId, { status: "synced", label: "Just now", last_sync_check_at: null });
            }
            else {
                showToast(result.message || "Save sync failed");
            }
        }
        catch {
            showToast("Save sync failed");
        }
        finally {
            setActionPending(null);
        }
    };
    const handleDownloadBios = async () => {
        if (actionPending || !detail.platformSlug)
            return;
        setActionPending("bios");
        try {
            const result = await downloadAllFirmware(detail.platformSlug);
            if (result.success) {
                showToast(`BIOS downloaded (${result.downloaded ?? 0} files)`);
                globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "bios", platform_slug: detail.platformSlug } }));
                await refreshBiosStatus(appId);
            }
            else {
                showToast(result.message || "BIOS download failed");
            }
        }
        catch {
            showToast("BIOS download failed");
        }
        finally {
            setActionPending(null);
        }
    };
    const handleUninstall = async () => {
        if (actionPending || !detail.romId)
            return;
        setActionPending("uninstall");
        const admission = capturePruneLeaseAdmission(`game-detail:${appId}`);
        try {
            const result = await removeRom(detail.romId);
            if (result.success) {
                await withPruneLease(result.prune_lease_token, "Game detail uninstall", async (signal) => {
                    if (isPruneLeaseCancelled(signal))
                        return;
                    await setLaunchOptionsConfirmed(appId, "").catch(() => false);
                    if (isPruneLeaseCancelled(signal))
                        return;
                    globalThis.dispatchEvent(new CustomEvent("romm_rom_uninstalled", { detail: { rom_id: detail.romId } }));
                }, `game-detail:${appId}`, admission);
                showToast(`${detail.romName || "ROM"} uninstalled`);
            }
            else {
                showToast(result.message || "Uninstall failed");
            }
        }
        catch (e) {
            if (isPruneLeaseCancellation(e, admission)) {
                detach(debugLog(`handleUninstall: continuation was cancelled: ${e}`));
                return;
            }
            showToast("Uninstall failed");
        }
        finally {
            setActionPending(null);
        }
    };
    const handleDeleteSaves = () => {
        if (actionPending || !detail.romId)
            return;
        const romId = detail.romId;
        DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Delete Local Saves", strDescription: "This will delete local save files for this game. Make sure saves are synced to RomM first \u2014 the next sync will re-download them from the server.", strOKButtonText: "Delete", strCancelButtonText: "Cancel", onOK: () => {
                detach((async () => {
                    setActionPending("deletesaves");
                    try {
                        const result = await deleteLocalSaves(romId);
                        if (result.success) {
                            showToast(result.message);
                            noteSaveSyncDisplay(appId, romId, { status: "none", label: "No saves", last_sync_check_at: null });
                            globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "save_sync", rom_id: romId } }));
                        }
                        else {
                            showToast(result.message || "Failed to delete saves");
                        }
                    }
                    catch {
                        showToast("Failed to delete saves");
                    }
                    finally {
                        setActionPending(null);
                    }
                })());
            } }));
    };
    const refreshCoreDisplay = async (platformSlug) => {
        await refreshCoreAndBios(appId);
        globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "core_changed", platform_slug: platformSlug } }));
    };
    const applyCoreResult = async (result, platformSlug, successBody, admission) => {
        await withPruneLease(result.prune_lease_token, "Core selection", async (signal) => {
            if (!result.success) {
                showToast(result.message || "Failed to set core");
                return;
            }
            if (result.launch_options !== undefined && result.app_id != null) {
                if (isPruneLeaseCancelled(signal))
                    return;
                const confirmed = await setLaunchOptionsConfirmed(result.app_id, result.launch_options);
                if (isPruneLeaseCancelled(signal))
                    return;
                if (!confirmed) {
                    showToast("Core saved — restart Steam to apply");
                    return;
                }
            }
            showToast(successBody);
            await refreshCoreDisplay(platformSlug);
        }, `game-detail:${appId}`, admission);
    };
    const handleChangeGameCore = async (coreLabel) => {
        const romId = detail.romId;
        if (!romId || !detail.platformSlug)
            return;
        const platformSlug = detail.platformSlug;
        detach(debugLog(`handleChangeGameCore: romId=${romId} coreLabel=${coreLabel}`));
        const admission = capturePruneLeaseAdmission(`game-detail:${appId}`);
        try {
            const result = await setGameCore(romId, coreLabel);
            detach(debugLog(`handleChangeGameCore: result success=${result.success}`));
            await applyCoreResult(result, platformSlug, `Core set to ${coreLabel}`, admission);
        }
        catch (e) {
            if (isPruneLeaseCancellation(e, admission)) {
                detach(debugLog(`handleChangeGameCore: continuation was cancelled: ${e}`));
                return;
            }
            showToast("Failed to set core");
        }
    };
    const handleResetGameCore = async () => {
        const romId = detail.romId;
        if (!romId || !detail.platformSlug)
            return;
        const platformSlug = detail.platformSlug;
        detach(debugLog(`handleResetGameCore: romId=${romId}`));
        const admission = capturePruneLeaseAdmission(`game-detail:${appId}`);
        try {
            const result = await clearGameCore(romId);
            detach(debugLog(`handleResetGameCore: result success=${result.success}`));
            await applyCoreResult(result, platformSlug, "Now following the system core", admission);
        }
        catch (e) {
            if (isPruneLeaseCancellation(e, admission)) {
                detach(debugLog(`handleResetGameCore: continuation was cancelled: ${e}`));
                return;
            }
            showToast("Failed to reset core");
        }
    };
    const showCoreMenu = (e) => {
        DFL.showContextMenu(buildEmulatorMenu({
            emulators: detail.emulators,
            emulatorDataAvailable: detail.emulatorDataAvailable,
            activeLabel: detail.activeCoreLabel,
            platformCoreLabel: detail.platformCoreLabel,
            followSystem: {
                hasGameOverride: detail.hasGameOverride,
                onFollowSystem: () => {
                    detach(handleResetGameCore());
                },
            },
            onPick: (label) => {
                detach(handleChangeGameCore(label));
            },
        }), getEventTarget(e));
    };
    const showRomMMenu = (e) => {
        DFL.showContextMenu(SP_JSX.jsxs(DFL.Menu, { label: "RomM Actions", children: [SP_JSX.jsx(DFL.MenuItem, { onClick: () => {
                        detach(handleRefreshArtwork());
                    }, children: "Refresh Artwork" }, "refresh-artwork"), SP_JSX.jsx(DFL.MenuItem, { onClick: () => {
                        detach(handleRefreshMetadata());
                    }, children: "Refresh Metadata" }, "refresh-metadata"), SP_JSX.jsx(DFL.MenuItem, { onClick: () => {
                        detach(handleSyncSaves());
                    }, children: "Sync Save Files" }, "sync-saves"), SP_JSX.jsx(DFL.MenuItem, { onClick: () => {
                        detach(handleDownloadBios());
                    }, children: "Download BIOS" }, "download-bios"), SP_JSX.jsx(DFL.MenuSeparator, {}, "sep"), SP_JSX.jsx(DFL.MenuItem, { tone: "destructive", onClick: handleDeleteSaves, children: "Delete Local Saves" }, "delete-saves"), SP_JSX.jsx(DFL.MenuItem, { tone: "destructive", onClick: () => {
                        detach(handleUninstall());
                    }, children: "Uninstall" }, "uninstall")] }), getEventTarget(e));
    };
    const showSteamMenu = (e) => {
        DFL.showContextMenu(SP_JSX.jsx(DFL.Menu, { label: "Steam", children: SP_JSX.jsx(DFL.MenuItem, { onClick: () => {
                    SteamClient.Apps.OpenAppSettingsDialog(appId, "general");
                }, children: "Properties" }, "properties") }), getEventTarget(e));
    };
    if (versionError) {
        return null;
    }
    if (migration.pending) {
        return null;
    }
    const infoItems = [];
    if (connectionState === "offline") {
        infoItems.push(SP_JSX.jsxs("div", { className: "romm-info-item", children: [SP_JSX.jsx("div", { className: "romm-info-header", children: SP_JSX.jsx(FaExclamationTriangle, { size: 12, color: "#ff8800" }) }), SP_JSX.jsx("div", { className: "romm-info-value", style: { color: "#ff8800" }, children: "RomM offline" })] }, "offline-indicator"));
    }
    if (!detail.installed && detail.fsSizeBytes != null) {
        infoItems.push(infoItem("space-required", "SPACE REQUIRED", formatBytes$1(detail.fsSizeBytes)));
    }
    if (playtimeInfo.lastPlayed) {
        infoItems.push(infoItem("last-played", "LAST PLAYED", playtimeInfo.lastPlayed));
    }
    if (playtimeInfo.playtime) {
        infoItems.push(infoItem("playtime", "PLAYTIME", playtimeInfo.playtime));
    }
    if (detail.raId) {
        const hasEarned = detail.achievementEarned > 0;
        const countLabel = detail.achievementTotal > 0 ? `${detail.achievementEarned}/${detail.achievementTotal}` : `${detail.achievementEarned}`;
        const sparklePositions = [
            { top: "5%", left: "80%" },
            { top: "70%", left: "10%" },
            { top: "15%", left: "35%" },
            { top: "85%", left: "70%" },
            { top: "45%", left: "90%" },
        ];
        const sparkleDurs = [2.4, 3.5, 2.8, 3.8, 3.1];
        const sparkleDelays = [0, 0.9, 0.3, 1.6, 1.1];
        const sparkleDots = hasEarned
            ? sparklePositions.map((pos, i) => {
                const dotStyle = {
                    "--romm-sparkle-top": pos.top,
                    "--romm-sparkle-left": pos.left,
                    "--romm-sparkle-delay": `${sparkleDelays[i]}s`,
                    "--romm-sparkle-dur": `${sparkleDurs[i]}s`,
                };
                return SP_JSX.jsx("span", { className: "romm-sparkle-dot", style: dotStyle }, `sparkle-${pos.top}-${pos.left}`);
            })
            : [];
        infoItems.push(SP_JSX.jsxs("div", { className: "romm-info-item romm-cheevo-badge", onClick: () => {
                globalThis.dispatchEvent(new CustomEvent("romm_tab_switch", { detail: { tab: "achievements" } }));
            }, children: [SP_JSX.jsx("div", { className: "romm-info-header", children: "ACHIEVEMENTS" }), SP_JSX.jsxs("div", { className: "romm-cheevo-badge-sparkle", children: [SP_JSX.jsxs("span", { style: { position: "relative", display: "inline-block" }, children: [SP_JSX.jsx("span", { className: hasEarned ? "romm-cheevo-trophy" : "romm-cheevo-trophy-none", children: "\uD83C\uDFC6" }), hasEarned ? SP_JSX.jsx("span", { className: "romm-sparkle-container", children: sparkleDots }) : null] }), SP_JSX.jsx("span", { className: "romm-cheevo-count", children: countLabel })] })] }, "achievements"));
    }
    if (detail.activeSlot == null && detail.saveSyncEnabled) {
        infoItems.push(SP_JSX.jsxs("div", { className: "romm-info-item", children: [SP_JSX.jsx("div", { className: "romm-info-header", children: "SAVE SYNC" }), SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#ff8800", marginTop: "4px" }, children: "\u26A0 Legacy save slot" })] }, "legacy-slot-warning"));
    }
    if (detail.biosRequiredMissing) {
        infoItems.push(SP_JSX.jsxs("div", { className: "romm-info-item", onClick: () => {
                globalThis.dispatchEvent(new CustomEvent("romm_tab_switch", { detail: { tab: "bios" } }));
            }, style: { cursor: "pointer" }, children: [SP_JSX.jsx("div", { className: "romm-info-header", children: "BIOS" }), SP_JSX.jsxs("div", { className: "romm-info-value", style: { display: "flex", alignItems: "center", gap: "6px" }, children: [SP_JSX.jsx("span", { className: "romm-status-dot", style: { backgroundColor: BIOS_MISSING_RED } }), detail.biosLabel] })] }, "bios"));
    }
    const playSectionRow = (SP_JSX.jsxs(DFL.Focusable, { "data-romm": "true", className: `romm-play-section-row ${basicAppDetailsSectionStylerClasses?.PlaySection || ""}`.trim(), "flow-children": "right", style: {
            display: "flex",
            alignItems: "center",
            gap: "20px",
            padding: "16px 2.8vw",
            background: "rgba(14, 20, 27, 0.33)",
            boxSizing: "border-box",
        }, children: [SP_JSX.jsx(CustomPlayButton, { appId: appId }), SP_JSX.jsx(DiscSelector, { appId: appId }), SP_JSX.jsx(VersionPicker, { appId: appId }), SP_JSX.jsx("div", { className: "romm-info-items", style: {
                    display: "flex",
                    alignItems: "center",
                    gap: "20px",
                    flexWrap: "nowrap",
                    overflow: "hidden",
                }, children: infoItems }), SP_JSX.jsxs("div", { style: {
                    marginLeft: "auto",
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    flexShrink: 0,
                }, children: [SP_JSX.jsx(DFL.DialogButton, { className: "romm-gear-btn", onClick: showRomMMenu, onFocus: scrollToTop, title: "RomM Actions", children: SP_JSX.jsx(FaGamepad, { size: 18, color: "#553e98" }) }), detail.emulators.length > 1 ? (SP_JSX.jsx(DFL.DialogButton, { className: "romm-gear-btn", onClick: showCoreMenu, onFocus: scrollToTop, title: "Emulator Core", children: SP_JSX.jsx(FaMicrochip, { size: 18, color: detail.activeCoreIsDefault ? "#8f98a0" : "#d4a72c" }) }, "core-btn")) : null, SP_JSX.jsx(DFL.DialogButton, { className: "romm-gear-btn", onClick: showSteamMenu, onFocus: scrollToTop, title: "Steam Properties", children: SP_JSX.jsx(FaCog, { size: 18, color: "#8f98a0" }) })] })] }, "play-row"));
    return (SP_JSX.jsxs(SP_REACT.Fragment, { children: [detail.savefilesInContentDir && detail.saveSyncEnabled ? (SP_JSX.jsx(WarningCard, { title: "Save sync off", message: "RetroArch's 'Write Saves to Content Directory' is enabled, so saves go next to the ROM and can't be synced. Turn it off in RetroArch \u2192 Settings \u2192 Saving to re-enable save sync." }, "savefiles-content-dir-warning")) : null, playSectionRow] }));
};

const MUTED_COLOR = "#8f98a0";
function displaySlot(slot) {
    if (slot === null || slot === undefined || slot === "")
        return "Legacy";
    return slot;
}
function formatRelativeTime$1(isoStr) {
    if (!isoStr)
        return "";
    const date = new Date(isoStr);
    if (Number.isNaN(date.getTime()))
        return "";
    const diffMs = Date.now() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1)
        return "just now";
    if (diffMin < 60)
        return `${diffMin}m ago`;
    if (diffMin < 1440)
        return `${Math.floor(diffMin / 60)}h ago`;
    const d = date.getDate();
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return `${d} ${months[date.getMonth()]}`;
}
function pickLastSyncer(syncs) {
    if (!syncs || syncs.length === 0)
        return null;
    return syncs.reduce((latest, ds) => {
        if (!latest)
            return ds;
        if (!ds.last_synced_at)
            return latest;
        if (!latest.last_synced_at)
            return ds;
        return ds.last_synced_at > latest.last_synced_at ? ds : latest;
    }, null);
}
function attributionLabel(uploadedByUs) {
    if (uploadedByUs === true)
        return "(this device)";
    if (uploadedByUs === false)
        return "(not this device)";
    return null;
}
function formatAttributionSegment(uploadedByUs, deviceName, showCheck = true) {
    const check = showCheck ? " ✓" : "";
    const label = attributionLabel(uploadedByUs);
    if (uploadedByUs === true) {
        return deviceName ? `${deviceName} ${label}${check}` : `${label}${check}`;
    }
    if (uploadedByUs === false) {
        return `${label}${check}`;
    }
    if (label === null) {
        if (deviceName)
            return `${deviceName}${check}`;
        return showCheck ? "✓" : null;
    }
    return null;
}
function slotDeleteFailureToast(info) {
    if (info.reason === "active_slot" || info.is_active) {
        return "Cannot delete the active slot. Switch to a different slot first.";
    }
    if (info.reason === "server_unreachable") {
        return info.message ?? "Cannot inspect slot — RomM server is not reachable";
    }
    return info.message ?? "Cannot delete this slot";
}
function statusLabel(status, lastSyncAt) {
    switch (status) {
        case "synced":
        case "skip":
            return { color: "#5ba32b", label: "Synced" };
        case "upload":
            return { color: "#d4a72c", label: "Local changes" };
        case "download":
            return { color: "#1a9fff", label: "Server newer" };
        case "conflict":
            return { color: "#d94126", label: "Conflict" };
        case "unknown":
            return { color: "#8f98a0", label: "Status unknown" };
        default:
            if (lastSyncAt)
                return { color: "#5ba32b", label: "Synced" };
            return { color: "#8f98a0", label: "Not synced" };
    }
}
function computeSyncSummary(isActive, saveStatus, conflicts) {
    if (!isActive || !saveStatus)
        return { syncSummaryText: null, syncSummaryColor: MUTED_COLOR };
    if (saveStatus.server_query_failed) {
        const text = saveStatus.server_query_reason === "server_unreachable" ? "Server unreachable" : "Save status unavailable";
        return { syncSummaryText: text, syncSummaryColor: MUTED_COLOR };
    }
    const hasConflict = conflicts.length > 0;
    const files = saveStatus.files;
    if (hasConflict)
        return { syncSummaryText: "Conflict detected", syncSummaryColor: "#d94126" };
    if (files.length === 0)
        return { syncSummaryText: "No saves found", syncSummaryColor: MUTED_COLOR };
    if (files.some((f) => f.status === "upload")) {
        return { syncSummaryText: "Local changes", syncSummaryColor: "#d4a72c" };
    }
    if (files.some((f) => f.status === "download")) {
        return { syncSummaryText: "Server newer", syncSummaryColor: "#1a9fff" };
    }
    if (saveStatus.last_sync_check_at) {
        const rel = formatRelativeTime$1(saveStatus.last_sync_check_at);
        return { syncSummaryText: rel === "just now" ? "Synced just now" : `Synced ${rel}`, syncSummaryColor: "#5ba32b" };
    }
    return { syncSummaryText: "Not synced", syncSummaryColor: MUTED_COLOR };
}

const ConnectingIndicator = ({ label = "Connecting to RomM" }) => {
    const progress = useServerRetryProgress();
    const text = progress ? `${label}… (attempt ${progress.attempt}/${progress.maxAttempts})` : `${label}…`;
    return (SP_JSX.jsxs("div", { style: { display: "flex", alignItems: "center", gap: "8px", padding: "8px 0" }, children: [SP_JSX.jsx("span", { className: "romm-throbber", style: { width: "14px", height: "14px" } }), SP_JSX.jsx("span", { style: { fontSize: "13px", color: MUTED_COLOR }, children: text })] }));
};

function formatCheevoDate(dateStr) {
    return dateStr.replace(/:\d{2}$/, "");
}
function makeHcSparkles(seed) {
    const rng = (i) => {
        const x = Math.sin(seed * 9301 + i * 4973) * 49297;
        return x - Math.floor(x);
    };
    return Array.from({ length: 4 }, (_, i) => ({
        top: `${Math.round(rng(i * 3) * 100)}%`,
        left: `${Math.round(rng(i * 3 + 1) * 100)}%`,
        dur: 2.2 + rng(i * 3 + 2) * 1.8,
        delay: rng(i * 7 + 5) * 2,
    }));
}
function renderCheevoRow(a, earnedMap) {
    const earnedData = earnedMap.get(a.badge_id);
    const isEarned = !!earnedData;
    const isHardcore = !!earnedData?.date_hardcore;
    const rowClasses = ["romm-cheevo-row", isEarned ? "romm-cheevo-row-earned" : ""].filter(Boolean).join(" ");
    const imgClasses = ["romm-cheevo-badge-img", isHardcore ? "romm-cheevo-badge-img-hc" : ""].filter(Boolean).join(" ");
    const dateChildren = [];
    if (earnedData?.date) {
        dateChildren.push(SP_JSX.jsx("span", { className: "romm-cheevo-date", children: formatCheevoDate(earnedData.date) }, "date"));
    }
    if (isHardcore && earnedData.date_hardcore) {
        dateChildren.push(SP_JSX.jsxs("span", { style: { display: "inline-flex", alignItems: "center", gap: "4px" }, children: [SP_JSX.jsx("span", { className: "romm-cheevo-hc-badge", children: "HC" }), SP_JSX.jsx("span", { className: "romm-cheevo-date", children: formatCheevoDate(earnedData.date_hardcore) })] }, "hc-row"));
    }
    const imgEl = (SP_JSX.jsx("img", { alt: "", className: imgClasses, src: isEarned ? a.badge_url : a.badge_url_lock || a.badge_url, style: isEarned ? {} : { filter: "grayscale(0.7) opacity(0.6)" } }));
    const badgeElement = isHardcore ? (SP_JSX.jsxs("div", { className: "romm-cheevo-img-wrap", children: [imgEl, SP_JSX.jsx("span", { className: "romm-cheevo-img-sparkles", children: makeHcSparkles(a.ra_id).map((sp) => {
                    const sparkleStyle = {
                        "--romm-sparkle-top": sp.top,
                        "--romm-sparkle-left": sp.left,
                        "--romm-sparkle-delay": `${sp.delay.toFixed(1)}s`,
                        "--romm-sparkle-dur": `${sp.dur.toFixed(1)}s`,
                    };
                    return (SP_JSX.jsx("span", { className: "romm-cheevo-img-sparkle-dot", style: sparkleStyle }, `hc-sp-${sp.top}-${sp.left}`));
                }) })] })) : (imgEl);
    return (SP_JSX.jsxs(DFL.DialogButton, { className: rowClasses, noFocusRing: false, onFocus: scrollFocusedToCenter, style: {
            background: "transparent",
            border: "none",
            padding: 0,
            textAlign: "left",
            cursor: "default",
            display: "flex",
            alignItems: "center",
            gap: "12px",
        }, children: [badgeElement, SP_JSX.jsxs("div", { className: "romm-cheevo-details", children: [SP_JSX.jsx("div", { className: "romm-cheevo-title", children: a.title }), SP_JSX.jsx("div", { className: "romm-cheevo-desc", children: a.description }), a.num_awarded > 0 ? SP_JSX.jsx("div", { className: "romm-cheevo-rarity", children: `${a.num_awarded} players earned this` }) : null] }), dateChildren.length > 0 ? SP_JSX.jsx("div", { className: "romm-cheevo-dates", children: dateChildren }) : null, SP_JSX.jsx("div", { className: `romm-cheevo-points ${isEarned ? "" : "romm-cheevo-points-locked"}`, children: `${a.points} pts` })] }, `cheevo-${a.ra_id}`));
}
function renderCheevoList(achievements, progress) {
    const earned = progress?.earned ?? 0;
    const total = progress?.total ?? achievements.length;
    const earnedMap = new Map();
    for (const ea of progress?.earned_achievements ?? []) {
        earnedMap.set(ea.id, ea);
    }
    const sorted = [...achievements].sort((a, b) => {
        const aEarned = earnedMap.has(a.badge_id) ? 0 : 1;
        const bEarned = earnedMap.has(b.badge_id) ? 0 : 1;
        if (aEarned !== bEarned)
            return aEarned - bEarned;
        return (a.display_order || 0) - (b.display_order || 0);
    });
    const earnedList = sorted.filter((a) => earnedMap.has(a.badge_id));
    const lockedList = sorted.filter((a) => !earnedMap.has(a.badge_id));
    const cheevoChildren = [];
    cheevoChildren.push(SP_JSX.jsxs("div", { className: "romm-cheevo-summary", children: [SP_JSX.jsx("span", { className: "romm-cheevo-summary-text", children: `${earned} / ${total} Achievements` }), progress?.earned_hardcore ? (SP_JSX.jsx("span", { className: "romm-cheevo-summary-sub", children: `${progress.earned_hardcore} hardcore` })) : null] }, "summary"));
    const pct = total > 0 ? (earned / total) * 100 : 0;
    cheevoChildren.push(SP_JSX.jsx("div", { className: "romm-cheevo-progress-bar", children: SP_JSX.jsx("div", { className: "romm-cheevo-progress-fill", style: { width: `${pct}%` } }) }, "progress-bar"));
    if (earnedList.length > 0) {
        cheevoChildren.push(SP_JSX.jsx("div", { className: "romm-cheevo-section-title", children: `Earned (${earnedList.length})` }, "earned-title"));
        earnedList.forEach((a) => cheevoChildren.push(renderCheevoRow(a, earnedMap)));
    }
    if (lockedList.length > 0) {
        cheevoChildren.push(SP_JSX.jsx("div", { className: "romm-cheevo-section-title", children: `Locked (${lockedList.length})` }, "locked-title"));
        lockedList.forEach((a) => cheevoChildren.push(renderCheevoRow(a, earnedMap)));
    }
    return SP_JSX.jsx("div", { className: "romm-cheevo-list", children: cheevoChildren });
}
const AchievementsTab = ({ romId, raId, isActive }) => {
    const isOffline = useRommConnectionState() === "offline";
    const [achievements, setAchievements] = SP_REACT.useState([]);
    const [progress, setProgress] = SP_REACT.useState(null);
    const [loading, setLoading] = SP_REACT.useState(false);
    const loadedRef = SP_REACT.useRef(false);
    SP_REACT.useEffect(() => {
        if (!isActive || !raId)
            return;
        if (loadedRef.current)
            return;
        if (isOffline)
            return;
        loadedRef.current = true;
        const load = beginServerLoad();
        let cancelled = false;
        let settled = false;
        async function loadAchievements() {
            setServerRetryProgress(null);
            setLoading(true);
            try {
                const [listResult, progressResult] = await Promise.all([getAchievements(romId), getAchievementProgress(romId)]);
                if (cancelled)
                    return;
                settled = true;
                const unreachable = listResult.reason === "server_unreachable" || progressResult.reason === "server_unreachable";
                if (unreachable) {
                    reportServerReachable(false);
                    loadedRef.current = false;
                }
                else if ((listResult.success && !listResult.stale) || (progressResult.success && !progressResult.stale)) {
                    reportServerReachable(true);
                }
                if (listResult.success)
                    setAchievements(listResult.achievements);
                if (progressResult.success)
                    setProgress(progressResult);
                setLoading(false);
            }
            catch (e) {
                detach(debugLog(`Failed to load achievements: ${e}`));
                if (!cancelled) {
                    settled = true;
                    loadedRef.current = false;
                    setLoading(false);
                }
            }
            finally {
                settleServerLoad(load);
            }
        }
        detach(loadAchievements());
        return () => {
            cancelled = true;
            if (!settled) {
                loadedRef.current = false;
                setLoading(false);
            }
        };
    }, [isActive, raId, romId, isOffline]);
    if (!isActive)
        return null;
    if (loading) {
        return SP_JSX.jsx(ConnectingIndicator, { label: "Loading achievements" });
    }
    if (achievements.length === 0) {
        return (SP_JSX.jsx("div", { className: "romm-panel-muted", children: isOffline ? "RomM offline — achievements unavailable." : "No achievements found for this game" }));
    }
    return renderCheevoList(achievements, progress);
};

function isFetchable(file) {
    return file.on_server === true && !file.downloaded && file.declared_kind !== "directory";
}

const PATH_OBSTRUCTED = "firmware-path-obstructed";
const PATH_NOT_A_DIRECTORY = "firmware-path-not-a-directory";
const HOLDS_NO_IMAGE = ["firmware-directory-holds-no-image", "firmware-directory-holds-no-candidate"];
const IMAGE_CONTRADICTED = "firmware-image-contradicted";
const READ_INCOMPLETE = ["firmware-scan-incomplete", "firmware-unreadable"];
const PATH_INACCESSIBLE = "firmware-path-inaccessible";
function verdictNote(row) {
    const has = (code) => (row.caveats ?? []).includes(code);
    if (row.declared_kind !== "directory")
        return fileAtItsDestination(has, row.checked);
    if (row.satisfied === true)
        return folderHolding(row.images ?? []);
    if (row.satisfied === false)
        return folderUnmet(has);
    return folderWithheld(row.satisfied, has);
}
const said = (note) => ({ note, lines: [], fromLibrary: false });
function fileAtItsDestination(has, checked) {
    if (has(PATH_OBSTRUCTED))
        return said("a folder is here, where the emulator opens a file");
    if (has(PATH_INACCESSIBLE))
        return said("its location could not be read");
    if (checked === "unrecognised")
        return said("the emulator does not recognise this file");
    if (checked === "unread")
        return said("its bytes could not be read");
    if (checked === "refused")
        return said("the emulator refuses a file of this size");
    return said("");
}
function folderHolding(images) {
    return images.length > 0 ? { note: "", lines: [...images], fromLibrary: false } : said("holds a BIOS image");
}
function folderUnmet(has) {
    if (has(PATH_NOT_A_DIRECTORY))
        return said("a file is here, where the emulator opens a folder");
    return said(HOLDS_NO_IMAGE.some(has) ? "holds no BIOS image" : "");
}
function folderWithheld(satisfied, has) {
    if (has(IMAGE_CONTRADICTED))
        return said("holds an image that could not be confirmed");
    if (READ_INCOMPLETE.some(has))
        return said("its contents could not be read in full");
    return said(satisfied === null ? "its contents could not be checked" : "");
}
function biosFileDescription(file) {
    if (file.declared_kind === "directory")
        return null;
    if (file.declaration !== "read")
        return null;
    const description = file.description.trim();
    if (!description)
        return null;
    if (description.startsWith(`${file.file_name} `)) {
        return description.slice(file.file_name.length).trim() || null;
    }
    const [head, ...tail] = description.split(" ");
    const token = (head ?? "").replace(/^['"]|['"]$/g, "");
    if ((token.split("/").pop() ?? "") !== file.file_name)
        return description;
    const rest = tail.join(" ").trim();
    return rest || null;
}
function biosFileNote(row) {
    if (row.supplied_by)
        return { note: `provided by ${row.supplied_by}`, lines: [], fromLibrary: false };
    const verdict = verdictNote(row);
    if (verdict.note || verdict.lines.length > 0)
        return verdict;
    if (row.declared_kind === "directory")
        return { note: "", lines: [], fromLibrary: false };
    if (row.on_server === false) {
        return {
            note: row.downloaded ? "not in your RomM library" : "missing, not in your RomM library",
            lines: [],
            fromLibrary: true,
        };
    }
    return { note: "", lines: [], fromLibrary: false };
}

const HELD_RATIO_PHRASE = "files held";
function biosHeldRatio(source) {
    const total = source.server_count ?? 0;
    const done = source.local_count ?? 0;
    return total > 0 ? ` (${done}/${total} ${HELD_RATIO_PHRASE})` : "";
}

const ROLE_MID = "the launching emulator";
const ROLE_LEADING = "The launching emulator";
const CANNOT_START = "cannot start this system without a BIOS image";
const REQUIRES_UNCHECKED = "requires could not be checked";
const IMAGE_UNSETTLED_HEAD = "Whether the BIOS image";
const IMAGE_UNSETTLED_TAIL = "needs is in place could not be established";
const NOTHING_ESTABLISHED_HEAD = "Nothing could be established about what";
const NOTHING_ESTABLISHED_TAIL = "needs";
const REQUIRES_ARE_IN_PLACE = "requires are in place";
const REQUIRES_IS_IN_PLACE = "requires is in place";
const REQUIRES_IS_NOT_IN_PLACE = "requires is not in place";
const MARKS_NONE_REQUIRED = "marks none of its BIOS files as required";
const OPTIONAL_MISSING_TAIL = "optional missing";
const STATUS_NEEDS_IMAGE = "Needs a BIOS image";
const STATUS_READINESS_UNKNOWN = "Readiness unknown";
const STATUS_REQUIREMENT_UNKNOWN = "Requirement unknown";
const STATUS_NOTHING_REQUIRED = "Nothing required";
function biosSummary(source, rows, level) {
    const emulator = source.active_core_label ?? null;
    const named = emulator ?? ROLE_MID;
    const leading = emulator ?? ROLE_LEADING;
    const systemImage = source.system_image ?? "not_demanded";
    const withheld = source.required_withheld ?? 0;
    const requiredRows = rows.filter((row) => row.required_by_active);
    const requiredCount = source.required_count ?? requiredRows.length;
    const requiredDone = source.required_downloaded ?? requiredRows.filter((row) => row.downloaded).length;
    if (systemImage === "absent") {
        return { status: STATUS_NEEDS_IMAGE, sentence: `${leading} ${CANNOT_START}` };
    }
    if (level === "unknown") {
        return declinedSummary(named, withheld, systemImage);
    }
    if (requiredCount > 0) {
        return requiredFilesSummary(named, rows, requiredDone, requiredCount, level);
    }
    return { status: STATUS_NOTHING_REQUIRED, sentence: `${leading} ${MARKS_NONE_REQUIRED}` };
}
function declinedSummary(named, withheld, systemImage) {
    if (withheld > 0) {
        const files = withheld === 1 ? "One file" : `${withheld} files`;
        return {
            status: STATUS_READINESS_UNKNOWN,
            sentence: `${files} ${named} ${REQUIRES_UNCHECKED}`,
        };
    }
    if (systemImage === "unsettled") {
        return {
            status: STATUS_READINESS_UNKNOWN,
            sentence: `${IMAGE_UNSETTLED_HEAD} ${named} ${IMAGE_UNSETTLED_TAIL}`,
        };
    }
    return {
        status: STATUS_REQUIREMENT_UNKNOWN,
        sentence: `${NOTHING_ESTABLISHED_HEAD} ${named} ${NOTHING_ESTABLISHED_TAIL}`,
    };
}
function requiredFilesSummary(named, rows, requiredDone, requiredCount, level) {
    const ratio = `${requiredDone} / ${requiredCount} required`;
    const ready = level === null ? requiredDone >= requiredCount : level === "ok";
    const one = requiredCount === 1;
    if (ready) {
        const optionalMissing = rows.filter((row) => row.wanted === "optional" && !row.required_by_active && !row.downloaded).length;
        const tail = optionalMissing > 0 ? ` (${optionalMissing} ${OPTIONAL_MISSING_TAIL})` : "";
        const held = one
            ? `The one file ${named} ${REQUIRES_IS_IN_PLACE}`
            : `All ${requiredCount} files ${named} ${REQUIRES_ARE_IN_PLACE}`;
        return { status: ratio, sentence: `${held}${tail}` };
    }
    return {
        status: ratio,
        sentence: one
            ? `The one file ${named} ${REQUIRES_IS_NOT_IN_PLACE}`
            : `${requiredDone} of ${requiredCount} files ${named} ${REQUIRES_ARE_IN_PLACE}`,
    };
}

function infoRow$1(key, label, value) {
    return (SP_JSX.jsxs("div", { className: "romm-panel-info-row", children: [SP_JSX.jsx("span", { className: "romm-panel-label", children: label }), SP_JSX.jsx("span", { className: "romm-panel-value", children: value })] }, key));
}
function section(key, title, ...children) {
    return (SP_JSX.jsxs(DFL.DialogButton, { className: "romm-panel-section", style: {
            background: "transparent",
            border: "none",
            padding: "12px 0",
            textAlign: "left",
            width: "100%",
            cursor: "default",
            display: "block",
        }, noFocusRing: false, onFocus: scrollFocusedToCenter, children: [title ? SP_JSX.jsx("div", { className: "romm-panel-section-title", children: title }) : null, children.filter(Boolean)] }, key));
}

function coreLineSuffix(core) {
    if (core.required)
        return " (required)";
    if (core.needs_one_of != null)
        return ` (needs one of its ${core.needs_one_of} BIOS files)`;
    return " (optional)";
}
function fallbackEmulatorLabel(emulator) {
    return emulator.replace(/\.so$/, "").replace(/_libretro$/, "") || emulator;
}
function buildBiosCoreLines(cores, emulatorLabels, activeEmulator) {
    return Object.entries(cores).map(([emulator, coreData]) => {
        const label = emulatorLabels.get(emulator) || fallbackEmulatorLabel(emulator);
        const suffix = coreLineSuffix(coreData);
        const isActiveCore = emulator === activeEmulator;
        return (SP_JSX.jsx("div", { style: {
                color: isActiveCore ? "#d4a72c" : "rgba(255, 255, 255, 0.5)",
                fontSize: "12px",
                fontWeight: isActiveCore ? "bold" : "normal",
            }, children: `${label}${suffix}` }, `core-${emulator}`));
    });
}
function buildBiosHeader(bios, biosLevel) {
    const heldRatio = biosHeldRatio(bios);
    const biosColor = biosColorForLevel(biosLevel);
    const biosLabel = `${biosSummary(bios, bios.files ?? [], biosLevel).sentence}${heldRatio}`;
    return [
        SP_JSX.jsx("div", { className: "romm-panel-section-title", style: { marginBottom: "8px" }, children: "BIOS" }, "bios-title"),
        SP_JSX.jsxs("div", { className: "romm-panel-status-inline", children: [SP_JSX.jsx("span", { className: "romm-status-dot", style: { backgroundColor: biosColor } }), SP_JSX.jsx("span", { className: "romm-panel-value", children: biosLabel })] }, "bios-row"),
    ];
}
function rowVerdict$1(file) {
    return file.satisfied === undefined ? file.downloaded : file.satisfied;
}
function fileDotColor(file) {
    const verdict = rowVerdict$1(file);
    if (verdict === null)
        return "#d4a72c";
    if (verdict)
        return "#5ba32b";
    if (file.required_by_active)
        return "#d94126";
    const requiredElsewhere = Object.values(file.cores ?? {}).some((c) => c.required);
    return requiredElsewhere ? "#d4a72c" : "#8f98a0";
}
function fileLines(lines, coreLines) {
    if (lines.length === 0 && coreLines.length === 0)
        return null;
    return (SP_JSX.jsxs("div", { style: {
            flexBasis: "100%",
            display: "flex",
            flexDirection: "column",
            gap: "2px",
            marginLeft: "18px",
        }, children: [lines.map((line) => (SP_JSX.jsx("div", { style: { color: "rgba(255, 255, 255, 0.5)", fontSize: "12px", whiteSpace: "pre-wrap" }, children: line }, `image-${line}`))), coreLines] }, "lines"));
}
function rowBelongsOnThisPage(file) {
    if (file.required_by_active || file.system_image_candidate)
        return true;
    if (rowVerdict$1(file) !== false)
        return true;
    return isFetchable(file);
}
function buildBiosFileList(bios, coreInfo) {
    const emulatorLabels = new Map();
    for (const e of coreInfo?.emulators ?? []) {
        if (e.emulator && !emulatorLabels.has(e.emulator))
            emulatorLabels.set(e.emulator, e.label);
    }
    const files = bios.files ?? [];
    const wantedFiles = files.filter((f) => f.wanted === "needed" || f.wanted === "optional");
    const shownFiles = wantedFiles.filter(rowBelongsOnThisPage);
    const countOf = (wanted) => files.filter((f) => f.wanted === wanted).length;
    const fileElements = shownFiles.map((f) => {
        const coreLines = f.cores ? buildBiosCoreLines(f.cores, emulatorLabels, coreInfo?.active_core) : [];
        const { note, lines } = biosFileNote(f);
        const label = biosFileDescription(f);
        const suffix = note ? ` — ${note}` : "";
        return (SP_JSX.jsxs("div", { className: "romm-panel-file-row", children: [SP_JSX.jsx("span", { className: "romm-status-dot", style: { backgroundColor: fileDotColor(f) } }, "dot"), SP_JSX.jsxs("span", { className: "romm-panel-file-name", children: [f.declared_path || f.file_name, label !== null && SP_JSX.jsx("span", { style: { color: "rgba(255, 255, 255, 0.5)" }, children: ` ${label}` }, "label"), suffix] }, "name"), fileLines(lines, coreLines)] }, f.file_name));
    });
    const summaryLine = (key, text) => (SP_JSX.jsx("div", { className: "romm-panel-file-row", style: { color: "rgba(255, 255, 255, 0.4)", fontSize: "12px", marginTop: "8px" }, children: text }, key));
    const elsewhere = wantedFiles.length - shownFiles.length;
    if (elsewhere > 0) {
        fileElements.push(summaryLine("elsewhere-note", elsewhere === 1
            ? "1 more file an installed emulator asks for — not required for this launch, " +
                "nothing to download; the Library page's Platforms tab lists it"
            : `${elsewhere} more files an installed emulator asks for — none required for this launch, ` +
                "none to download; the Library page's Platforms tab lists them"));
    }
    for (const [wanted, phrase] of [
        ["not_needed", "no installed emulator asks for"],
        ["unknown", "nothing installed could answer for"],
    ]) {
        const count = countOf(wanted);
        if (count === 0)
            continue;
        fileElements.push(summaryLine(`${wanted}-note`, `${count} file${count === 1 ? "" : "s"} on server ${phrase}`));
    }
    return fileElements;
}
const BiosTab = ({ biosStatus, biosLevel, coreInfo, isActive }) => {
    if (!isActive || !biosStatus)
        return null;
    const biosColumn = buildBiosHeader(biosStatus, biosLevel);
    const fileElements = buildBiosFileList(biosStatus, coreInfo);
    if (fileElements.length > 0) {
        biosColumn.push(SP_JSX.jsx("div", { className: "romm-panel-file-list", children: fileElements }, "bios-file-list"));
    }
    const coreColumn = [
        SP_JSX.jsx("div", { className: "romm-panel-section-title", style: { marginBottom: "8px" }, children: "Emulator" }, "core-title"),
        infoRow$1("core", "Active Core", coreInfo?.active_core_label ? coreInfo.active_core_label : "Default"),
    ];
    return section("bios-core", null, SP_JSX.jsxs("div", { style: { display: "flex", gap: "24px" }, children: [SP_JSX.jsx("div", { style: { flex: 1, minWidth: 0 }, children: biosColumn }, "bios-col"), SP_JSX.jsx("div", { style: { flexShrink: 0, minWidth: "120px" }, children: coreColumn }, "core-col")] }, "bios-core-columns"));
};

const PanelTabBar = ({ activeTab, hasAchievements, hasSaves, hasBios, onSelect }) => {
    const tabs = [
        { id: "info", label: "GAME INFO", visible: true },
        { id: "achievements", label: "ACHIEVEMENTS", visible: hasAchievements },
        { id: "saves", label: "SAVES", visible: hasSaves },
        { id: "bios", label: "BIOS", visible: hasBios },
    ];
    return (SP_JSX.jsx(DFL.Focusable, { className: "romm-tab-bar", "flow-children": "right", "data-romm": "true", children: tabs
            .filter((t) => t.visible)
            .map((t) => (SP_JSX.jsx(DFL.DialogButton, { className: `romm-tab ${activeTab === t.id ? "romm-tab-active" : ""}`, onClick: () => onSelect(t.id), style: {
                background: "transparent",
                border: "none",
                borderBottom: activeTab === t.id ? "2px solid #1a9fff" : "2px solid transparent",
                padding: "10px 16px",
                minWidth: "auto",
                width: "auto",
            }, noFocusRing: false, children: t.label }, `tab-${t.id}`))) }));
};

const SaveSortWarning = () => (SP_JSX.jsxs("div", { style: {
        padding: "8px 12px",
        marginBottom: "12px",
        backgroundColor: "rgba(212, 167, 44, 0.15)",
        borderLeft: "3px solid #d4a72c",
        borderRadius: "4px",
    }, children: [SP_JSX.jsx("div", { style: { fontSize: "13px", fontWeight: "bold", color: "#d4a72c", marginBottom: "4px" }, children: "\u26A0\uFE0F RetroArch save sorting changed" }), SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)" }, children: "Save file paths may be incorrect. Go to Settings to migrate." })] }));

function lastKnownFrom(result) {
    const known = result.last_known;
    if (!known?.slots.length)
        return null;
    return { slots: known.slots, activeSlot: known.active_slot };
}
function applyRefreshSlotResult(slotResult, setter) {
    if (!slotResult.success) {
        const lastKnown = lastKnownFrom(slotResult);
        if (lastKnown)
            setter((prev) => ({ ...prev, lastKnownSlots: lastKnown }));
        return;
    }
    setter((prev) => ({
        ...prev,
        availableSlots: slotResult.slots,
        activeSlot: slotResult.active_slot === undefined ? prev.activeSlot : slotResult.active_slot,
        activeSlotKnown: slotResult.active_slot !== undefined || prev.activeSlotKnown,
        lastKnownSlots: null,
    }));
}
function applyLoadSlotsResult(result, setter, loadedRef, logError) {
    if (!result.success) {
        logError(`Failed to load save slots: ${result.message ?? result.reason ?? "unknown"}`);
        loadedRef.current = false;
        const lastKnown = lastKnownFrom(result);
        setter((prev) => ({ ...prev, slotsLoading: false, lastKnownSlots: lastKnown ?? prev.lastKnownSlots }));
        return;
    }
    setter((prev) => ({
        ...prev,
        activeSlot: result.active_slot === undefined ? prev.activeSlot : result.active_slot,
        activeSlotKnown: result.active_slot !== undefined || prev.activeSlotKnown,
        availableSlots: result.slots,
        slotsLoading: false,
        lastKnownSlots: null,
    }));
}

function bindRom(romId, romIdRef, cancelled, setter) {
    return {
        romId,
        write: (update) => {
            if (cancelled() || romIdRef.current !== romId)
                return;
            setter(update);
        },
    };
}
function bindRomInState(romId, setter) {
    return {
        romId,
        write: (update) => setter((prev) => {
            if (prev.romId !== romId)
                return prev;
            return typeof update === "function" ? update(prev) : update;
        }),
    };
}
function takeReadTicket(seqs, kind) {
    const ticket = ++seqs.current[kind];
    return () => seqs.current[kind] !== ticket;
}
function refreshSlotState(binding, readSeqs) {
    const trackingOvertaken = takeReadTicket(readSeqs, "slotTracking");
    const slotsOvertaken = takeReadTicket(readSeqs, "slots");
    isSaveTrackingConfigured(binding.romId)
        .then((result) => {
        if (trackingOvertaken())
            return;
        binding.write((prev) => ({ ...prev, slotConfirmed: result.configured }));
    })
        .catch(() => { });
    getSaveSlots(binding.romId)
        .then((slotResult) => {
        if (slotsOvertaken())
            return;
        applyRefreshSlotResult(slotResult, binding.write);
    })
        .catch(() => { });
}
function refreshInstalledRomInBackground(binding) {
    return getInstalledRom(binding.romId)
        .then((installed) => {
        if (installed) {
            binding.write((prev) => ({ ...prev, installedRom: installed }));
        }
    })
        .catch(() => { });
}
function refreshCoverArtInBackground(binding) {
    return getArtworkBase64(binding.romId)
        .then((result) => {
        if (result.base64) {
            binding.write((prev) => ({ ...prev, coverBase64: result.base64 }));
        }
    })
        .catch(() => { });
}
function refreshMetadataInBackground(binding) {
    return getRomMetadataShared(binding.romId)
        .then((meta) => binding.write((prev) => ({ ...prev, metadata: meta })))
        .catch(() => { });
}
const UNKNOWN_REQUIREMENT_STATUS = { needs_bios: false, bios_status_unknown: true };
function biosFieldsFromCache(cached) {
    if (cached.bios_status_unknown) {
        if (cached.bios_level !== "unknown")
            return null;
        return { biosStatus: UNKNOWN_REQUIREMENT_STATUS, biosLevel: "unknown" };
    }
    if (!cached.bios_status)
        return { biosStatus: null, biosLevel: null };
    return {
        biosStatus: { needs_bios: true, ...cached.bios_status },
        biosLevel: cached.bios_level ?? null,
    };
}
function unknownBiosFields() {
    return { biosStatus: UNKNOWN_REQUIREMENT_STATUS, biosLevel: "unknown" };
}
function refreshBiosIfStale(cached, binding, readSeqs, read) {
    const overtaken = takeReadTicket(readSeqs, "bios");
    if (!(cached.stale_fields ?? []).includes("bios"))
        return Promise.resolve();
    return read(binding.romId)
        .then((answer) => {
        if (overtaken())
            return;
        const biosFields = biosFieldsFromCache(answer);
        if (!biosFields)
            return;
        binding.write((prev) => ({ ...prev, ...biosFields }));
    })
        .catch((e) => detach(debugLog(`RomMGameInfoPanel: BIOS status refresh error: ${e}`)));
}
function saveStatusFromCache(romId, cachedSave) {
    if (!cachedSave)
        return null;
    return {
        rom_id: romId,
        files: cachedSave.files.map((f) => ({
            filename: f.filename,
            status: f.status,
            local_path: null,
            local_hash: null,
            local_mtime: null,
            local_size: null,
            server_save_id: null,
            server_file_name: null,
            server_emulator: null,
            server_updated_at: null,
            server_size: null,
            last_sync_at: f.last_sync_at ?? null,
        })),
        playtime: {
            total_seconds: 0,
            session_count: 0,
            last_session_start: null,
            last_session_duration_sec: null,
            last_played: null,
        },
        device_id: "",
        last_sync_check_at: cachedSave.last_sync_check_at ?? null,
    };
}
function startBackgroundRefreshes(cached, binding, readSeqs) {
    const bgPromises = [refreshBiosIfStale(cached, binding, readSeqs, getBiosStatusShared)];
    if (cached.installed) {
        bgPromises.push(refreshInstalledRomInBackground(binding));
    }
    bgPromises.push(refreshCoverArtInBackground(binding));
    const metaStale = cached.stale_fields?.includes("metadata") ?? true;
    if (!cached.metadata || metaStale) {
        bgPromises.push(refreshMetadataInBackground(binding));
    }
    if (binding.romId) {
        bgPromises.push(refreshPanelCoreInfo(binding));
    }
    return Promise.all(bgPromises);
}
function refreshPanelCoreInfo(binding) {
    return getPlatformCoreInfoShared(binding.romId)
        .then((coreInfo) => binding.write((prev) => ({ ...prev, coreInfo })))
        .catch(() => { });
}
async function loadData(appId, cancelled, romIdRef, platformSlugRef, readSeqs, setter) {
    const overtaken = takeReadTicket(readSeqs, "detail");
    try {
        const cached = await getCachedGameDetail(appId);
        if (cancelled() || overtaken())
            return;
        if (!cached.found) {
            setter((prev) => ({ ...prev, loading: false, error: true }));
            return;
        }
        const romId = cached.rom_id;
        const romName = cached.rom_name || "";
        const platformName = cached.platform_name || "";
        const platformSlug = cached.platform_slug || "";
        romIdRef.current = romId;
        platformSlugRef.current = platformSlug;
        const { biosStatus, biosLevel } = biosFieldsFromCache(cached) ?? { biosStatus: null, biosLevel: null };
        const saveStatus = saveStatusFromCache(romId, cached.save_status);
        const conflicts = cached.save_status?.conflicts ?? [];
        const raId = cached.ra_id ?? null;
        setter({
            loading: false,
            romId,
            romName,
            platformName,
            installed: cached.installed ?? false,
            installedRom: null,
            metadata: cached.metadata,
            coverBase64: null,
            biosStatus,
            biosLevel,
            coreInfo: null,
            saveSyncEnabled: cached.save_sync_enabled ?? false,
            saveStatus,
            conflicts,
            error: false,
            activeTab: "info",
            raId,
            slotConfirmed: false,
            activeSlot: "default",
            activeSlotKnown: false,
            availableSlots: [],
            lastKnownSlots: null,
            slotsLoading: false,
            regions: cached.regions ?? [],
            languages: cached.languages ?? [],
        });
        const binding = bindRom(romId, romIdRef, cancelled, setter);
        if (cached.save_sync_enabled) {
            refreshSlotState(binding, readSeqs);
        }
        await startBackgroundRefreshes(cached, binding, readSeqs);
    }
    catch (e) {
        detach(debugLog(`RomMGameInfoPanel: loadData error: ${e}`));
        if (!cancelled() && !overtaken())
            setter((prev) => ({ ...prev, loading: false, error: true }));
    }
}

function bindCurrentRom(ctx, romId) {
    return bindRom(romId, ctx.romIdRef, ctx.cancelled, ctx.setState);
}
async function handleSaveSyncSettingsChange(ctx, detail) {
    const enabled = detail.save_sync_enabled;
    if (!enabled) {
        takeReadTicket(ctx.readSeqs, "saveStatus");
        ctx.setState((prev) => ({
            ...prev,
            saveSyncEnabled: false,
            activeTab: prev.activeTab === "saves" ? "info" : prev.activeTab,
        }));
        return;
    }
    ctx.setState((prev) => ({ ...prev, saveSyncEnabled: true }));
    const romId = ctx.romIdRef.current;
    if (!romId)
        return;
    const binding = bindCurrentRom(ctx, romId);
    const overtaken = takeReadTicket(ctx.readSeqs, "saveStatus");
    const result = await getSaveStatus(binding.romId).catch(() => null);
    if (result && isCallableFailure(result))
        return;
    if (overtaken())
        return;
    const updatedStatus = result;
    const conflicts = updatedStatus?.conflicts ?? [];
    binding.write((prev) => ({
        ...prev,
        saveStatus: updatedStatus,
        conflicts,
    }));
}
async function handleSaveSyncChange(ctx, detail) {
    if (detail.rom_id && detail.rom_id !== ctx.romIdRef.current)
        return;
    const romId = ctx.romIdRef.current;
    if (!romId)
        return;
    const binding = bindCurrentRom(ctx, romId);
    const overtaken = takeReadTicket(ctx.readSeqs, "saveStatus");
    const result = detail.save_status ?? (await getSaveStatus(binding.romId).catch(() => null));
    if (result && isCallableFailure(result))
        return;
    const updatedStatus = result;
    const conflicts = updatedStatus?.conflicts ?? [];
    if (!overtaken()) {
        binding.write((prev) => ({
            ...prev,
            saveStatus: updatedStatus,
            conflicts,
        }));
    }
    refreshSlotState(binding, ctx.readSeqs);
}
async function handleBiosChange(ctx, detail) {
    if (!detail.platform_slug || detail.platform_slug !== ctx.platformSlugRef.current)
        return;
    const updated = await checkPlatformBios(detail.platform_slug).catch(() => null);
    if (ctx.cancelled() || !updated)
        return;
    if (updated.bios_status_unknown) {
        ctx.setState((prev) => ({ ...prev, ...unknownBiosFields() }));
        return;
    }
    const biosLevel = updated.needs_bios ? (updated.bios_level ?? null) : null;
    ctx.setState((prev) => ({ ...prev, biosStatus: updated.needs_bios ? updated : null, biosLevel }));
}
async function handleCoreChange(ctx, _detail) {
    invalidateCachedGameDetail(ctx.appId);
    const rid = ctx.romIdRef.current;
    if (!rid)
        return;
    const binding = bindCurrentRom(ctx, rid);
    const [coreInfo, cached] = await Promise.all([
        getPlatformCoreInfo(binding.romId).catch(() => null),
        getCachedGameDetail(ctx.appId),
    ]);
    if (ctx.cancelled() || ctx.romIdRef.current !== rid || !cached.found)
        return;
    const biosFields = biosFieldsFromCache(cached);
    binding.write((prev) => ({ ...prev, ...biosFields, coreInfo: coreInfo ?? prev.coreInfo }));
    await refreshBiosIfStale(cached, binding, ctx.readSeqs, getBiosStatus);
}
async function handleVersionSwitched(ctx, detail) {
    if (detail.app_id !== ctx.appId)
        return;
    const overtaken = takeReadTicket(ctx.readSeqs, "detail");
    const cached = await getCachedGameDetail(ctx.appId);
    if (ctx.cancelled() || overtaken() || !cached.found)
        return;
    const newRomId = cached.rom_id ?? ctx.romIdRef.current;
    ctx.romIdRef.current = newRomId;
    ctx.slotsLoadedRef.current = false;
    const saveStatus = newRomId != null ? saveStatusFromCache(newRomId, cached.save_status) : null;
    const biosFields = biosFieldsFromCache(cached);
    const saveSyncEnabled = cached.save_sync_enabled ?? false;
    ctx.setState((prev) => {
        const biosStatus = biosFields ? biosFields.biosStatus : prev.biosStatus;
        const activeTabGone = (prev.activeTab === "bios" && !biosStatus) || (prev.activeTab === "saves" && !saveSyncEnabled);
        return {
            ...prev,
            romId: newRomId,
            romName: cached.rom_name || prev.romName,
            installed: cached.installed ?? false,
            installedRom: null,
            regions: cached.regions ?? [],
            languages: cached.languages ?? [],
            saveSyncEnabled,
            saveStatus,
            conflicts: cached.save_status?.conflicts ?? [],
            raId: cached.ra_id ?? null,
            activeSlot: "default",
            activeSlotKnown: false,
            availableSlots: [],
            lastKnownSlots: null,
            slotsLoading: false,
            ...biosFields,
            activeTab: activeTabGone ? "info" : prev.activeTab,
        };
    });
    if (saveSyncEnabled && newRomId != null) {
        refreshSlotState(bindCurrentRom(ctx, newRomId), ctx.readSeqs);
    }
    if (newRomId) {
        const binding = bindCurrentRom(ctx, newRomId);
        const reads = [
            refreshBiosIfStale(cached, binding, ctx.readSeqs, getBiosStatus),
            refreshCoverArtInBackground(binding),
            refreshPanelCoreInfo(binding),
        ];
        if (cached.installed)
            reads.push(refreshInstalledRomInBackground(binding));
        await Promise.all(reads);
    }
}
async function handleMetadataChange(ctx, detail) {
    if (detail.rom_id !== ctx.romIdRef.current)
        return;
    const romId = ctx.romIdRef.current;
    if (!romId)
        return;
    const binding = bindCurrentRom(ctx, romId);
    const meta = await getRomMetadata(binding.romId).catch(() => null);
    binding.write((prev) => ({ ...prev, metadata: meta }));
}
async function handleCoverRefreshed(ctx, detail) {
    if (detail.rom_id !== ctx.romIdRef.current)
        return;
    const romId = ctx.romIdRef.current;
    if (!romId)
        return;
    await refreshCoverArtInBackground(bindCurrentRom(ctx, romId));
}
function dispatchDataChanged$1(ctx, detail) {
    if (!ctx.romIdRef.current)
        return Promise.resolve();
    switch (detail?.type) {
        case "save_sync_settings":
            return handleSaveSyncSettingsChange(ctx, detail);
        case "save_sync":
            return handleSaveSyncChange(ctx, detail);
        case "bios":
            return handleBiosChange(ctx, detail);
        case "core_changed":
            return handleCoreChange(ctx);
        case "metadata":
            return handleMetadataChange(ctx, detail);
        case "cover_refreshed":
            return handleCoverRefreshed(ctx, detail);
        case "version_switched":
            return handleVersionSwitched(ctx, detail);
        default:
            return Promise.resolve();
    }
}
function wirePanelEvents(ctx) {
    const onUninstall = (e) => {
        const detail = e.detail;
        if (detail?.rom_id === ctx.romIdRef.current) {
            ctx.setState((prev) => ({ ...prev, installed: false, installedRom: null }));
        }
    };
    globalThis.addEventListener("romm_rom_uninstalled", onUninstall);
    const onDownloadComplete = addEventListener("download_complete", (evt) => {
        if (evt.rom_id !== ctx.romIdRef.current)
            return;
        invalidateCachedGameDetail(ctx.appId);
        ctx.setState((prev) => ({ ...prev, installed: true }));
        detach(refreshInstalledRomInBackground(bindCurrentRom(ctx, evt.rom_id)));
    });
    const onDataChanged = (e) => {
        detach((async () => {
            try {
                await dispatchDataChanged$1(ctx, e.detail);
            }
            catch (err) {
                detach(debugLog(`RomMGameInfoPanel: onDataChanged error: ${err}`));
            }
        })());
    };
    globalThis.addEventListener("romm_data_changed", onDataChanged);
    const onTabSwitch = (e) => {
        const tab = e.detail?.tab;
        if (tab)
            ctx.setState((prev) => ({ ...prev, activeTab: tab }));
    };
    globalThis.addEventListener("romm_tab_switch", onTabSwitch);
    return () => {
        globalThis.removeEventListener("romm_rom_uninstalled", onUninstall);
        removeEventListener("download_complete", onDownloadComplete);
        globalThis.removeEventListener("romm_data_changed", onDataChanged);
        globalThis.removeEventListener("romm_tab_switch", onTabSwitch);
    };
}

async function fetchSlots(romId, run, slotsLoadedRef, readSeqs, setState) {
    const load = beginServerLoad();
    setServerRetryProgress(null);
    const slotsOvertaken = takeReadTicket(readSeqs, "slots");
    setState((prev) => ({ ...prev, slotsLoading: true }));
    try {
        const result = await getSaveSlots(romId);
        if (run.cancelled)
            return;
        run.settled = true;
        if (result.success) {
            reportServerReachable(true);
        }
        else if (result.reason === "server_unreachable") {
            reportServerReachable(false);
        }
        if (slotsOvertaken()) {
            if (!result.success)
                slotsLoadedRef.current = false;
            setState((prev) => ({ ...prev, slotsLoading: false }));
            return;
        }
        applyLoadSlotsResult(result, setState, slotsLoadedRef, (msg) => {
            detach(debugLog(msg));
        });
    }
    catch (e) {
        detach(debugLog(`Failed to load save slots: ${e}`));
        if (!run.cancelled) {
            run.settled = true;
            slotsLoadedRef.current = false;
            setState((prev) => ({ ...prev, slotsLoading: false }));
        }
    }
    finally {
        settleServerLoad(load);
    }
}
function releaseUnsettledRun(run, slotsLoadedRef, setState) {
    if (run.settled)
        return;
    slotsLoadedRef.current = false;
    setState((prev) => (prev.slotsLoading ? { ...prev, slotsLoading: false } : prev));
}
function useSaveSlotsLoad(state, slotsLoadedRef, readSeqs, setState) {
    const isOffline = useRommConnectionState() === "offline";
    const { activeTab, saveSyncEnabled, romId } = state;
    SP_REACT.useEffect(() => {
        if (activeTab !== "saves" || !saveSyncEnabled || !romId)
            return;
        if (slotsLoadedRef.current)
            return;
        if (isOffline)
            return;
        slotsLoadedRef.current = true;
        const run = { cancelled: false, settled: false };
        detach(fetchSlots(romId, run, slotsLoadedRef, readSeqs, setState));
        return () => {
            run.cancelled = true;
            releaseUnsettledRun(run, slotsLoadedRef, setState);
        };
    }, [activeTab, saveSyncEnabled, romId, isOffline, slotsLoadedRef, readSeqs, setState]);
}

function formatReleaseDate(timestamp) {
    if (!timestamp || timestamp <= 0)
        return null;
    const date = new Date(timestamp * 1000);
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
}
function metadataRows(meta, platformName) {
    const rows = [];
    if (meta.summary) {
        rows.push(SP_JSX.jsx("div", { className: "romm-panel-summary", children: meta.summary }, "summary"));
    }
    if (platformName) {
        rows.push(infoRow$1("platform", "Platform", platformName));
    }
    if (meta.companies.length > 0) {
        rows.push(infoRow$1("companies", "Developer / Publisher", meta.companies.join(", ")));
    }
    if (meta.genres.length > 0) {
        rows.push(SP_JSX.jsxs("div", { className: "romm-panel-info-row", children: [SP_JSX.jsx("span", { className: "romm-panel-label", children: "Genres" }), SP_JSX.jsx("div", { className: "romm-panel-tags", children: meta.genres.map((g) => (SP_JSX.jsx("span", { className: "romm-panel-tag", children: g }, g))) })] }, "genres"));
    }
    const releaseDate = formatReleaseDate(meta.first_release_date);
    if (releaseDate) {
        rows.push(infoRow$1("release-date", "Release Date", releaseDate));
    }
    if (meta.game_modes.length > 0) {
        rows.push(infoRow$1("game-modes", "Game Modes", meta.game_modes.join(", ")));
    }
    if (meta.player_count) {
        rows.push(infoRow$1("players", "Players", meta.player_count));
    }
    if (meta.average_rating != null && meta.average_rating > 0) {
        rows.push(infoRow$1("rating", "Rating", `${Math.round(meta.average_rating)}%`));
    }
    return rows;
}
function gameInfoRows(props) {
    const rows = [];
    if (props.romName) {
        rows.push(SP_JSX.jsx("div", { className: "romm-panel-rom-name", children: props.romName }, "rom-name"));
    }
    if (props.regions.length > 0) {
        rows.push(infoRow$1("regions", "Region", props.regions.join("/")));
    }
    if (props.languages.length > 0) {
        rows.push(infoRow$1("languages", "Languages", props.languages.join(", ")));
    }
    if (props.metadata) {
        rows.push(...metadataRows(props.metadata, props.platformName));
    }
    else if (props.platformName) {
        rows.push(infoRow$1("platform", "Platform", props.platformName));
    }
    if (rows.length === 0) {
        rows.push(SP_JSX.jsx("div", { className: "romm-panel-muted", children: "No metadata available" }, "no-meta"));
    }
    return rows;
}
function romFileSection(installed, installedRom) {
    if (!installed || !installedRom)
        return null;
    const noLaunchTargetNote = installedRom.launchable ? null : (SP_JSX.jsx("div", { className: "romm-panel-muted", style: { marginTop: "4px" }, children: `Downloaded, but nothing here is a format ${installedRom.system} can launch — no launch ` +
            `command was set. The files are on disk; install them in the emulator to play.` }, "no-launch-target"));
    return section("rom-file", "ROM File", infoRow$1("filename", "Filename", installedRom.file_name), noLaunchTargetNote);
}
const GameInfoTab = (props) => {
    const rows = gameInfoRows(props);
    const gameInfoSection = props.coverBase64
        ? section("game-info", null, SP_JSX.jsxs("div", { style: { display: "flex", gap: "16px", alignItems: "flex-start" }, children: [SP_JSX.jsx("img", { alt: "", src: `data:image/png;base64,${props.coverBase64}`, style: { width: "120px", borderRadius: "4px", flexShrink: 0, objectFit: "cover" } }, "cover"), SP_JSX.jsx("div", { style: { flex: 1 }, children: rows }, "details")] }, "game-info-row"))
        : section("game-info", null, ...rows);
    return (SP_JSX.jsxs("div", { children: [gameInfoSection, romFileSection(props.installed, props.installedRom)] }));
};

const STALE_NOTE = "Slots as RomM last reported them — counts and times are from that answer, not from now.";
function renderSlotRow(slot, isActive) {
    const badges = [
        isActive ? (SP_JSX.jsx("span", { className: "romm-slot-badge romm-slot-badge-active", children: "active" }, "active")) : null,
        SP_JSX.jsx("span", { className: `romm-slot-badge romm-slot-badge-${slot.source}`, children: slot.source }, "src"),
    ];
    return (SP_JSX.jsxs("div", { "data-testid": `last-known-slot-${slot.slot || "legacy"}`, className: "romm-slot-panel", children: [SP_JSX.jsxs("div", { className: "romm-slot-header-static", children: [SP_JSX.jsxs("div", { className: "romm-slot-header-left", children: [SP_JSX.jsx("span", { className: "romm-slot-name", children: displaySlot(slot.slot) }), badges] }), SP_JSX.jsx("div", { className: "romm-slot-header-right", children: SP_JSX.jsx("span", { className: "romm-slot-count", children: `${slot.count} save${slot.count === 1 ? "" : "s"}` }) })] }), slot.latest_updated_at ? (SP_JSX.jsx("div", { className: "romm-slot-stale-detail", children: `Newest save: ${formatTimestamp$2(slot.latest_updated_at)}` })) : null] }, `last-known-${slot.slot}`));
}
function renderLastKnownSlots(lastKnown) {
    const activeKey = lastKnown.activeSlot ?? "";
    return (SP_JSX.jsxs("div", { "data-testid": "last-known-slots", children: [SP_JSX.jsx("div", { className: "romm-slot-stale-note", children: STALE_NOTE }), SP_JSX.jsx("div", { className: "romm-slot-stale", children: lastKnown.slots.map((slot) => renderSlotRow(slot, slot.slot === activeKey)) })] }, "last-known-slots"));
}

const NewSlotModal = ({ closeModal, onSubmit }) => {
    const [value, setValue] = SP_REACT.useState("");
    return (SP_JSX.jsx(DFL.ConfirmModal, { ...(closeModal !== undefined ? { closeModal } : {}), onOK: () => {
            onSubmit(value.trim());
        }, strTitle: "New Save Slot", bDisableBackgroundDismiss: true, bOKDisabled: value.trim() === "", children: SP_JSX.jsx(DFL.TextField, { focusOnMount: true, label: "Slot Name", value: value, onChange: (e) => setValue(e.target.value), onKeyDown: (e) => {
                if (e.key === "Enter" && value.trim() !== "") {
                    onSubmit(value.trim());
                    closeModal?.();
                }
            } }) }));
};

const LABEL_WIDTH = "88px";
function infoRow(key, label, value, valueColor = "#c7cdd3") {
    if (value == null || value === "")
        return null;
    return (SP_JSX.jsxs("div", { style: { display: "flex", alignItems: "flex-start", fontSize: "11px", marginTop: "2px" }, children: [SP_JSX.jsx("span", { style: { color: "#697075", width: LABEL_WIDTH, flexShrink: 0 }, children: label }), SP_JSX.jsx("div", { style: { color: valueColor, flex: 1, minWidth: 0 }, children: value })] }, key));
}
function buildLastSyncedValue(f, isSynced) {
    const lastSyncer = pickLastSyncer(f.device_syncs);
    const pieces = [f.last_sync_at ? formatRelativeTime$1(f.last_sync_at) || "Never" : "Never"];
    const attrSegment = formatAttributionSegment(f.uploaded_by_us, lastSyncer?.device_name, isSynced);
    if (attrSegment !== null)
        pieces.push(attrSegment);
    if (f.is_current === false) {
        pieces.push("Newer version available on server");
    }
    return pieces.join(" · ");
}
function renderSaveFileRow(f, conflict, lastSyncCheckAt) {
    const { color, label } = statusLabel(f.status, f.last_sync_at);
    const isSynced = f.status === "synced" || f.status === "skip";
    const conflictActive = f.status === "conflict" || !!conflict;
    const checkedHint = !isSynced && lastSyncCheckAt ? formatRelativeTime$1(lastSyncCheckAt) : null;
    const headerMeta = [];
    if (f.local_size != null) {
        headerMeta.push(SP_JSX.jsx("span", { style: { fontSize: "11px", color: "#8f98a0" }, children: formatBytes$1(f.local_size) }, "size"));
    }
    headerMeta.push(SP_JSX.jsx("span", { className: "romm-save-status-label", style: { color, fontSize: "11px", fontWeight: 600 }, children: label }, "status"));
    const lastSyncedValue = buildLastSyncedValue(f, isSynced);
    const serverValueLines = [];
    if (f.server_save_id != null) {
        const headerParts = [`#${f.server_save_id}`];
        if (f.server_emulator)
            headerParts.push(f.server_emulator);
        serverValueLines.push(SP_JSX.jsx("div", { style: { color: "#c7cdd3" }, children: headerParts.join(" · ") }, "srv-head"));
        if (f.server_file_name) {
            serverValueLines.push(SP_JSX.jsx("div", { style: { color: "#8f98a0", fontFamily: "monospace", wordBreak: "break-all", marginTop: "1px" }, children: f.server_file_name }, "srv-fn"));
        }
    }
    return (SP_JSX.jsxs(DFL.DialogButton, { style: {
            background: "transparent",
            border: "none",
            padding: "8px 0",
            textAlign: "left",
            width: "100%",
            cursor: "default",
            display: "block",
        }, noFocusRing: false, onFocus: scrollFocusedToCenter, children: [SP_JSX.jsxs("div", { style: {
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: "8px",
                    marginBottom: "4px",
                }, children: [SP_JSX.jsx("div", { style: {
                            fontSize: "13px",
                            color: "#dcdedf",
                            fontWeight: 600,
                            overflow: "hidden",
                            textOverflow: "ellipsis",
                            whiteSpace: "nowrap",
                            flex: 1,
                            minWidth: 0,
                        }, children: f.filename }), SP_JSX.jsx("div", { style: { display: "flex", alignItems: "center", gap: "8px", flexShrink: 0 }, children: headerMeta })] }), conflictActive ? (SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#d94126", fontWeight: 600, marginTop: "2px", marginBottom: "2px" }, children: "Conflict detected \u2014 resolve from the sync action" })) : null, infoRow("last-synced", "Last synced:", lastSyncedValue), checkedHint ? infoRow("checked", "Checked:", checkedHint, "#8f98a0") : null, infoRow("last-updated", "Last updated:", f.server_updated_at ? formatTimestamp$2(f.server_updated_at) : null, "#8f98a0"), serverValueLines.length > 0 ? infoRow("server", "Server save:", SP_JSX.jsx("div", { children: serverValueLines })) : null, f.local_path
                ? infoRow("path", "Local path:", SP_JSX.jsx("span", { style: { fontFamily: "monospace", wordBreak: "break-all" }, children: f.local_path }), "#5a6066")
                : null] }, f.filename));
}

function renderCopyToSlotButton(key, saveId, copy) {
    return (SP_JSX.jsx(DFL.DialogButton, { style: {
            padding: "2px 8px",
            minWidth: "auto",
            fontSize: "11px",
            width: "auto",
            flexShrink: 0,
        }, noFocusRing: false, onFocus: scrollFocusedToCenter, disabled: copy.isOffline, onClick: () => {
            copy.onCopy(saveId, copy.sourceSlot);
        }, children: "Copy to slot\u2026" }, key));
}

function renderServerSaveRow(f, copy) {
    const details = [`#${f.id}`];
    if (f.size != null)
        details.push(formatBytes$1(f.size));
    if (f.updated_at)
        details.push(`Updated ${formatRelativeTime$1(f.updated_at)}`);
    return (SP_JSX.jsxs("div", { style: {
            padding: "4px 0",
            borderBottom: "1px solid rgba(255,255,255,0.04)",
            display: "flex",
            alignItems: "flex-start",
            gap: "8px",
        }, children: [SP_JSX.jsxs("div", { style: { flex: 1, minWidth: 0 }, children: [SP_JSX.jsx("div", { style: { fontSize: "12px", color: "#dcdedf", fontWeight: 500 }, children: f.filename }), details.length > 0 ? (SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#8f98a0", marginTop: "2px" }, children: details.join(" · ") })) : null] }), copy ? renderCopyToSlotButton(`copy-${f.id}`, f.id, copy) : null] }, `server-${f.id}`));
}

const InactiveSlotBody = ({ loadingSlot, slotFiles, switching, switchError, isOffline, isLegacy, handleActivate, handleDelete, deleting, copy, }) => {
    const children = [];
    if (loadingSlot) {
        children.push(SP_JSX.jsx("div", { style: { fontSize: "13px", color: MUTED_COLOR }, children: "Loading..." }, "loading"));
    }
    else if (slotFiles && slotFiles.length > 0) {
        for (const f of slotFiles) {
            children.push(renderServerSaveRow(f, copy));
        }
    }
    else if (slotFiles !== null) {
        children.push(SP_JSX.jsx("div", { style: { fontSize: "13px", color: MUTED_COLOR, fontStyle: "italic" }, children: "No saves in this slot" }, "no-server-files"));
    }
    if (!isLegacy) {
        const activateLabel = switching ? "Switching..." : "Activate Slot";
        const deleteLabel = deleting ? "Deleting..." : "Delete Slot";
        children.push(SP_JSX.jsxs(DFL.Focusable, { "flow-children": "right", style: { marginTop: "10px", display: "flex", gap: "8px", alignItems: "center" }, children: [SP_JSX.jsx(DFL.DialogButton, { style: { padding: "4px 12px", minWidth: "auto", fontSize: "12px", width: "auto" }, noFocusRing: false, onFocus: scrollFocusedToCenter, disabled: switching || isOffline, onClick: handleActivate, children: activateLabel }, "activate-btn"), SP_JSX.jsx(DFL.DialogButton, { style: { padding: "4px 12px", minWidth: "auto", fontSize: "12px", width: "auto", color: "#d94126" }, noFocusRing: false, onFocus: scrollFocusedToCenter, disabled: deleting || switching, onClick: handleDelete, children: deleteLabel }, "delete-btn")] }, "activate-row"), isOffline ? (SP_JSX.jsx("div", { style: { fontSize: "11px", color: MUTED_COLOR, fontStyle: "italic", marginTop: "4px" }, children: "Offline \u2014 slot switching unavailable" }, "offline-hint")) : null, switchError ? (SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#d94126", marginTop: "4px" }, children: switchError }, "switch-error")) : null);
    }
    return SP_JSX.jsx("div", { className: "romm-slot-body", children: children.filter(Boolean) });
};

const VersionHistoryPanel = ({ romId, slot, filename, isOffline, onRestored, onCopy, }) => {
    const [expanded, setExpanded] = SP_REACT.useState(false);
    const [versions, setVersions] = SP_REACT.useState(null);
    const [loading, setLoading] = SP_REACT.useState(false);
    const [restoring, setRestoring] = SP_REACT.useState(null);
    const [loadError, setLoadError] = SP_REACT.useState(null);
    const loadVersions = async () => {
        setLoading(true);
        setLoadError(null);
        try {
            const result = await savesListFileVersions(romId, slot, filename);
            if (result.status === "ok" || result.status === "multi_file_unsupported") {
                setVersions(result.versions);
            }
            else if (result.status === "not_found") {
                detach(debugLog(`VersionHistoryPanel: server has no such entry for ${filename}: ${result.message}`));
                setVersions(null);
                setLoadError("RomM couldn't find this game's save data.");
            }
            else {
                detach(debugLog(`VersionHistoryPanel: server unreachable for ${filename}: ${result.message}`));
                setVersions(null);
                setLoadError("Couldn't reach RomM. Tap retry.");
            }
        }
        catch (e) {
            detach(debugLog(`VersionHistoryPanel: failed to load versions for ${filename}: ${e}`));
            setVersions(null);
            setLoadError("Couldn't reach RomM. Tap retry.");
        }
        finally {
            setLoading(false);
        }
    };
    const handleToggle = async () => {
        const willExpand = !expanded;
        setExpanded(willExpand);
        if (willExpand && versions === null && loadError === null && !isOffline) {
            await loadVersions();
        }
    };
    SP_REACT.useEffect(() => {
        const onDataChanged = (e) => {
            const detail = e.detail;
            if (detail?.rom_id !== romId)
                return;
            setVersions(null);
            setLoadError(null);
            if (expanded && !isOffline)
                detach(loadVersions());
        };
        globalThis.addEventListener("romm_data_changed", onDataChanged);
        return () => globalThis.removeEventListener("romm_data_changed", onDataChanged);
    }, [romId, isOffline, expanded]);
    const handleRestore = async (version) => {
        setRestoring(version.id);
        try {
            const result = await savesRollbackToVersion(romId, slot, version.id);
            if (result.status === "ok") {
                showToast(`Save restored from ${formatRelativeTime$1(version.updated_at)}`);
                setVersions(null);
                setExpanded(false);
                onRestored();
            }
            else if (result.status === "conflict_blocked") {
                const first = result.conflicts[0];
                if (first) {
                    await showSyncConflictModal(first);
                }
                else {
                    showToast("Restore blocked by a sync conflict. Sync this save, then try again.");
                }
            }
            else if (result.status === "preflight_failed") {
                const detail = result.errors[0] ?? "preflight error";
                showToast(`Sync failed before restore: ${detail}`);
            }
            else if (result.status === "put_failed") {
                showToast("Restored locally, but the server didn't update. Other devices will see the previous version until you retry.");
                setVersions(null);
                setExpanded(false);
                onRestored();
            }
            else if (result.status === "rom_not_installed") {
                showToast("ROM is no longer installed locally. Reinstall and try again.");
            }
            else if (result.status === "version_deleted") {
                showToast("This version no longer exists on the server");
            }
            else if (result.status === "server_unreachable") {
                showToast("Couldn't reach RomM. Check your connection and try again.");
            }
            else if (result.status === "not_found") {
                showToast("RomM couldn't find this game's save data — nothing was restored.");
            }
            else if (result.status === "unsupported") {
                showToast("Version history requires RomM 4.7+");
            }
        }
        catch (e) {
            detach(debugLog(`VersionHistoryPanel: restore error for save ${version.id}: ${e}`));
        }
        finally {
            setRestoring(null);
        }
    };
    const versionCount = versions?.length ?? 0;
    const renderVersionRow = (v) => {
        const lastSyncer = pickLastSyncer(v.device_syncs);
        const deviceName = lastSyncer?.device_name ?? null;
        const isThisRestoring = restoring === v.id;
        const headerParts = [`#${v.id}`];
        if (v.emulator)
            headerParts.push(v.emulator);
        if (v.file_size_bytes != null)
            headerParts.push(formatBytes$1(v.file_size_bytes));
        const lastUpdatedParts = [formatTimestamp$2(v.updated_at)];
        const attrSegment = formatAttributionSegment(v.uploaded_by_us, deviceName);
        if (attrSegment !== null)
            lastUpdatedParts.push(attrSegment);
        return (SP_JSX.jsxs("div", { style: {
                display: "flex",
                alignItems: "flex-start",
                gap: "8px",
                padding: "6px 0",
                borderBottom: "1px solid rgba(255,255,255,0.06)",
            }, children: [SP_JSX.jsxs("div", { style: { flex: 1, minWidth: 0 }, children: [SP_JSX.jsx("div", { style: { fontSize: "12px", color: "#c7cdd3", fontWeight: 600 }, children: headerParts.join(" · ") }), SP_JSX.jsxs("div", { style: {
                                fontSize: "11px",
                                color: "#8f98a0",
                                marginTop: "2px",
                            }, children: [SP_JSX.jsx("span", { style: { color: "#697075" }, children: "Last updated: " }), lastUpdatedParts.join(" · ")] }), SP_JSX.jsx("div", { style: {
                                fontSize: "11px",
                                color: "#8f98a0",
                                fontFamily: "monospace",
                                wordBreak: "break-all",
                                marginTop: "2px",
                            }, children: v.file_name })] }), SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "4px", flexShrink: 0 }, children: [SP_JSX.jsx(DFL.DialogButton, { style: {
                                padding: "2px 8px",
                                minWidth: "auto",
                                fontSize: "11px",
                                width: "auto",
                                flexShrink: 0,
                            }, noFocusRing: false, onFocus: scrollFocusedToCenter, disabled: isThisRestoring || restoring !== null || isOffline, onClick: () => {
                                detach(handleRestore(v));
                            }, children: isThisRestoring ? "Restoring..." : "Restore" }, "restore"), onCopy ? renderCopyToSlotButton(`copy-ver-${v.id}`, v.id, { onCopy, sourceSlot: slot, isOffline }) : null] })] }, `ver-${v.id}`));
    };
    const renderBody = () => {
        if (isOffline) {
            return (SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#8f98a0", fontStyle: "italic" }, children: "Offline \u2014 versions unavailable" }));
        }
        if (loading) {
            return SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#8f98a0" }, children: "Loading..." });
        }
        if (loadError !== null) {
            return (SP_JSX.jsxs("div", { style: { display: "flex", alignItems: "center", gap: "8px" }, children: [SP_JSX.jsx("span", { style: { fontSize: "11px", color: "#c46161", fontStyle: "italic" }, children: loadError }), SP_JSX.jsx(DFL.DialogButton, { style: { padding: "2px 8px", minWidth: "auto", fontSize: "11px", width: "auto", flexShrink: 0 }, noFocusRing: false, onFocus: scrollFocusedToCenter, onClick: () => {
                            detach(loadVersions());
                        }, children: "Retry" })] }));
        }
        if (versionCount === 0) {
            return (SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#8f98a0", fontStyle: "italic" }, children: "No older versions available" }));
        }
        return (versions ?? []).map(renderVersionRow);
    };
    return (SP_JSX.jsxs("div", { style: { marginTop: "4px", marginLeft: "8px" }, children: [SP_JSX.jsxs(DFL.DialogButton, { style: {
                    background: "transparent",
                    border: "none",
                    padding: "2px 0",
                    textAlign: "left",
                    width: "100%",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    fontSize: "11px",
                    color: "#8f98a0",
                }, noFocusRing: false, onFocus: scrollFocusedToCenter, onClick: () => {
                    detach(handleToggle());
                }, children: [SP_JSX.jsx("span", { children: expanded ? "▾" : "▸" }), SP_JSX.jsx("span", { children: expanded && versions !== null ? `Previous Versions (${versionCount})` : "Previous Versions" })] }), expanded ? SP_JSX.jsx("div", { style: { marginTop: "4px" }, children: renderBody() }) : null] }, `history-${filename}`));
};

function renderMultiFileNote(componentFiles) {
    const n = componentFiles.length;
    return (SP_JSX.jsxs("div", { style: { marginTop: "6px", marginLeft: "8px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#8f98a0", fontWeight: 600 }, children: `Files in this save (${n})` }), componentFiles.map((fn) => (SP_JSX.jsx("div", { style: {
                    fontSize: "11px",
                    color: "#8f98a0",
                    fontFamily: "monospace",
                    wordBreak: "break-all",
                    marginTop: "1px",
                }, children: fn }, `comp-${fn}`))), SP_JSX.jsx("div", { style: { fontSize: "11px", color: MUTED_COLOR, fontStyle: "italic", marginTop: "4px" }, children: `This save spans ${n} files. Per-version rollback isn't available for multi-file saves yet.` })] }, "multi-file-note"));
}
function renderActiveSlotBody(saveStatus, conflicts, romId, slot, isOffline, onVersionRestored, onCopy) {
    if (saveStatus && saveStatus.files.length > 0) {
        if (saveStatus.multi_file) {
            const componentFiles = saveStatus.component_files ?? [];
            return [
                ...saveStatus.files.map((f) => {
                    const conflict = conflicts.find((c) => c.filename === f.filename);
                    return SP_JSX.jsx("div", { children: renderSaveFileRow(f, conflict, saveStatus.last_sync_check_at) }, f.filename);
                }),
                renderMultiFileNote(componentFiles),
            ];
        }
        return saveStatus.files.map((f) => {
            const conflict = conflicts.find((c) => c.filename === f.filename);
            return (SP_JSX.jsxs("div", { children: [renderSaveFileRow(f, conflict, saveStatus.last_sync_check_at), f.server_save_id != null ? (SP_JSX.jsx("div", { style: { display: "flex", justifyContent: "flex-end", marginTop: "4px" }, children: renderCopyToSlotButton(`copy-active-${f.filename}`, f.server_save_id, {
                            onCopy,
                            sourceSlot: slot,
                            isOffline,
                        }) }, `copy-active-${f.filename}`)) : null, SP_JSX.jsx(VersionHistoryPanel, { romId: romId, slot: slot, filename: f.filename, isOffline: isOffline, onRestored: onVersionRestored, onCopy: onCopy }, `vhp-${f.filename}`)] }, f.filename));
        });
    }
    return [
        SP_JSX.jsx("div", { style: { fontSize: "13px", color: MUTED_COLOR, fontStyle: "italic" }, children: "No save files tracked yet" }, "no-files"),
    ];
}
const SlotPanel = ({ romId, slot, isActive, defaultExpanded, saveStatus, conflicts, isOffline, onSlotSwitched, onVersionRestored, onSlotDeleted, onCopy, }) => {
    const [expanded, setExpanded] = SP_REACT.useState(defaultExpanded);
    const [slotFiles, setSlotFiles] = SP_REACT.useState(null);
    const [loadingSlot, setLoadingSlot] = SP_REACT.useState(false);
    const [switching, setSwitching] = SP_REACT.useState(false);
    const [switchError, setSwitchError] = SP_REACT.useState(null);
    const [deleting, setDeleting] = SP_REACT.useState(false);
    const switchErrorTimerRef = SP_REACT.useRef(null);
    SP_REACT.useEffect(() => {
        return () => {
            if (switchErrorTimerRef.current)
                clearTimeout(switchErrorTimerRef.current);
        };
    }, []);
    const slotName = slot.slot;
    const handleToggle = async () => {
        const willExpand = !expanded;
        setExpanded(willExpand);
        if (willExpand && !isActive && slotFiles === null) {
            setLoadingSlot(true);
            try {
                const result = await getSlotSaves(romId, slotName);
                setSlotFiles(result.success ? result.saves : []);
            }
            catch (e) {
                detach(debugLog(`SavesTab: failed to load slot saves for ${slotName}: ${e}`));
                setSlotFiles([]);
            }
            finally {
                setLoadingSlot(false);
            }
        }
    };
    const handleActivate = async () => {
        setSwitching(true);
        setSwitchError(null);
        try {
            const result = await switchSlot(romId, slotName);
            if (result.success && result.save_status) {
                reportServerReachable(true);
                onSlotSwitched(slotName, result.save_status);
            }
            else {
                let msg = "Failed to switch slot";
                if (result.reason === "pending_uploads") {
                    msg = "Sync your saves first — local changes haven't been uploaded";
                }
                else if (result.reason === "server_unreachable") {
                    reportServerReachable(false);
                    msg = "Can't switch — RomM server is not reachable";
                }
                else if (result.reason === "not_installed") {
                    msg = "Can't switch — download the game first";
                }
                setSwitchError(msg);
                if (switchErrorTimerRef.current)
                    clearTimeout(switchErrorTimerRef.current);
                switchErrorTimerRef.current = setTimeout(() => setSwitchError(null), 5000);
            }
        }
        catch (e) {
            detach(debugLog(`SavesTab: switchSlot error: ${e}`));
            setSwitchError("An error occurred while switching slots");
            if (switchErrorTimerRef.current)
                clearTimeout(switchErrorTimerRef.current);
            switchErrorTimerRef.current = setTimeout(() => setSwitchError(null), 5000);
        }
        finally {
            setSwitching(false);
        }
    };
    const handleDelete = async () => {
        setDeleting(true);
        try {
            const info = await getSlotDeleteInfo(romId, slotName);
            if (!info.success) {
                showToast(slotDeleteFailureToast(info));
                return;
            }
            const lines = [];
            if (info.source === "server" && (info.server_save_count ?? 0) > 0) {
                const n = info.server_save_count ?? 0;
                lines.push(`This will permanently delete ${n} save${n === 1 ? "" : "s"} from slot '${info.slot}' on the RomM server.`);
            }
            else {
                lines.push(`This will remove slot '${info.slot}' from your local configuration.`);
            }
            if ((info.local_file_count ?? 0) > 0) {
                const n = info.local_file_count ?? 0;
                lines.push(`${n} tracked file${n === 1 ? "" : "s"} will be unlinked.`);
            }
            lines.push("This cannot be undone.");
            DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Delete Slot", strDescription: lines.join("\n\n"), strOKButtonText: "Delete", strCancelButtonText: "Cancel", onOK: () => {
                    detach((async () => {
                        try {
                            const result = await deleteSlot(romId, slotName);
                            if (result.success) {
                                showToast(`Slot '${slotName}' deleted`);
                                onSlotDeleted();
                            }
                            else {
                                showToast(result.message ?? "Failed to delete slot");
                            }
                        }
                        catch (e) {
                            detach(debugLog(`SavesTab: deleteSlot error: ${e}`));
                            showToast("An error occurred while deleting the slot");
                        }
                    })());
                } }));
        }
        catch (e) {
            detach(debugLog(`SavesTab: getSlotDeleteInfo error: ${e}`));
            showToast("Failed to load slot info");
        }
        finally {
            setDeleting(false);
        }
    };
    const { syncSummaryText, syncSummaryColor } = computeSyncSummary(isActive, saveStatus, conflicts);
    const fileCount = isActive ? slot.count || (saveStatus?.files.length ?? 0) : (slotFiles?.length ?? slot.count);
    const isLegacy = slotName === "";
    const panelClasses = [
        "romm-slot-panel",
        isActive ? "romm-slot-panel-active" : "",
        isLegacy ? "romm-slot-panel-legacy" : "",
    ]
        .filter(Boolean)
        .join(" ");
    const sourceBadge = slot.source === "local" ? (SP_JSX.jsx("span", { className: "romm-slot-badge romm-slot-badge-local", children: "local" }, "src")) : (SP_JSX.jsx("span", { className: "romm-slot-badge romm-slot-badge-server", children: "server" }, "src"));
    const headerEl = (SP_JSX.jsxs(DFL.DialogButton, { className: "romm-slot-header", style: {
            background: "transparent",
            border: "none",
            padding: "10px 12px",
            textAlign: "left",
            width: "100%",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
        }, noFocusRing: false, onFocus: scrollFocusedToCenter, onClick: () => {
            detach(handleToggle());
        }, children: [SP_JSX.jsxs("div", { className: "romm-slot-header-left", children: [SP_JSX.jsx("span", { className: "romm-slot-name", children: displaySlot(slotName) }), isActive ? (SP_JSX.jsx("span", { className: "romm-slot-badge romm-slot-badge-active", children: "active" }, "active")) : null, sourceBadge] }), SP_JSX.jsxs("div", { className: "romm-slot-header-right", children: [SP_JSX.jsx("span", { className: "romm-slot-count", children: `${fileCount} save${fileCount === 1 ? "" : "s"}` }), SP_JSX.jsx("span", { className: "romm-slot-chevron", children: expanded ? "▾" : "▸" })] })] }, "header"));
    const syncSummaryEl = isActive && syncSummaryText ? (SP_JSX.jsx("div", { className: "romm-slot-sync-summary", style: { color: syncSummaryColor }, children: syncSummaryText }, "sync-summary")) : null;
    const legacyNoteEl = isLegacy ? (SP_JSX.jsx("div", { className: "romm-slot-legacy-note", children: "Used by the RomM web player. Read-only here \u2014 manage in the RomM web app." }, "legacy-note")) : null;
    let bodyEl = null;
    if (expanded) {
        bodyEl = isActive ? (SP_JSX.jsx("div", { className: "romm-slot-body", children: renderActiveSlotBody(saveStatus, conflicts, romId, slotName, isOffline, onVersionRestored, onCopy).filter(Boolean) }, "body")) : (SP_JSX.jsx(InactiveSlotBody, { loadingSlot: loadingSlot, slotFiles: slotFiles, switching: switching, switchError: switchError, isOffline: isOffline, isLegacy: isLegacy, deleting: deleting, handleActivate: () => {
                detach(handleActivate());
            }, handleDelete: () => {
                detach(handleDelete());
            }, copy: { onCopy, sourceSlot: slotName, isOffline } }, "body"));
    }
    return (SP_JSX.jsxs("div", { className: panelClasses, children: [headerEl, syncSummaryEl, legacyNoteEl, bodyEl] }, `slot-${slotName}`));
};

const CopyToSlotModal = ({ availableSlots, sourceSlot, onSubmit, closeModal }) => {
    const [newName, setNewName] = SP_REACT.useState("");
    const targetSlots = Array.from(new Set(availableSlots.map((s) => s.slot).filter((name) => name !== "" && name !== sourceSlot))).sort((a, b) => a.localeCompare(b));
    const pick = (target) => {
        const trimmed = target.trim();
        if (!trimmed)
            return;
        closeModal?.();
        onSubmit(trimmed);
    };
    const existingRows = targetSlots.length > 0
        ? targetSlots.map((name) => (SP_JSX.jsx(DFL.DialogButton, { style: { padding: "6px 12px", width: "100%", textAlign: "left" }, onClick: () => {
                pick(name);
            }, children: displaySlot(name) }, `target-${name}`)))
        : [
            SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255,255,255,0.5)", fontStyle: "italic" }, children: "No other slots yet \u2014 create one below." }, "no-existing"),
        ];
    return (SP_JSX.jsx(DFL.ModalRoot, { ...(closeModal !== undefined ? { closeModal } : {}), children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "320px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "16px", fontWeight: "bold", marginBottom: "4px", color: "#fff" }, children: "Copy save to slot" }), SP_JSX.jsx("div", { style: { fontSize: "13px", color: "rgba(255,255,255,0.6)", marginBottom: "16px", lineHeight: "1.4" }, children: "Copies this save into the chosen slot, which becomes the active slot. The original save is kept." }), SP_JSX.jsx("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: existingRows }), SP_JSX.jsxs("div", { style: { marginTop: "16px" }, children: [SP_JSX.jsx(DFL.TextField, { focusOnMount: false, label: "New slot\u2026", value: newName, onChange: (e) => setNewName(e.target.value), onKeyDown: (e) => {
                                if (e.key === "Enter")
                                    pick(newName);
                            } }), SP_JSX.jsx(DFL.DialogButton, { style: { marginTop: "8px", padding: "6px 12px", width: "100%" }, disabled: newName.trim() === "", onClick: () => {
                                pick(newName);
                            }, children: "Create & copy here" })] })] }) }));
};

function dispatchDataChanged(romId) {
    globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "save_sync", rom_id: romId } }));
}
async function handleResult(result, target, romId) {
    switch (result.status) {
        case "ok":
            showToast(`Save copied to slot '${displaySlot(target)}'`);
            dispatchDataChanged(romId);
            return;
        case "already_present":
            showToast(`Already in slot '${displaySlot(target)}' as #${result.existing_id}`);
            return;
        case "conflict_blocked": {
            const first = result.conflicts[0];
            if (first) {
                await showSyncConflictModal(first);
            }
            else {
                showToast("Copy blocked by a sync conflict. Sync this save, then try again.");
            }
            return;
        }
        case "target_slot_busy":
            showToast(`Slot '${displaySlot(target)}' has newer changes on another device — sync it first, then copy again.`);
            return;
        case "preflight_failed":
            showToast(`Sync failed before copy: ${result.errors[0] ?? "preflight error"}`);
            return;
        case "server_unreachable":
            showToast("Couldn't reach RomM. Check your connection and try again.");
            return;
        case "not_found":
            showToast("RomM couldn't find this game's save data — nothing was copied.");
            return;
        case "version_deleted":
            showToast("This save no longer exists on the server.");
            return;
        case "rom_not_installed":
            showToast("ROM is no longer installed locally. Reinstall and try again.");
            return;
        case "unsupported":
            showToast(result.reason === "savefiles_in_content_dir"
                ? "Save sync is off for this game (RetroArch writes saves next to the ROM)."
                : "Copying isn't available for multi-file saves yet.");
            return;
        case "not_configured":
            showToast("Set up save slots for this game first, then copy.");
            return;
        case "copy_failed":
            showToast(`Couldn't copy the save: ${result.message}`);
            return;
        case "invalid_slot_name":
            showToast("Enter a valid slot name.");
            return;
    }
}
function useCopyToSlot(romId, availableSlots) {
    return SP_REACT.useCallback((saveId, sourceSlot) => {
        const runCopy = async (target) => {
            try {
                const result = await copySaveToSlot(romId, saveId, target);
                await handleResult(result, target, romId);
            }
            catch (e) {
                detach(debugLog(`useCopyToSlot: copy failed for save ${saveId} into '${target}': ${e}`));
                showToast("Couldn't copy the save. Check your connection and try again.");
            }
        };
        DFL.showModal(SP_JSX.jsx(CopyToSlotModal, { availableSlots: availableSlots, sourceSlot: sourceSlot, onSubmit: (target) => {
                detach(runCopy(target));
            } }));
    }, [romId, availableSlots]);
}

const SavesTab = ({ appId, romId, saveStatus, conflicts, activeSlot, activeSlotKnown, availableSlots, lastKnownSlots, slotsLoading, onSlotSwitched, }) => {
    const [newSlotError, setNewSlotError] = SP_REACT.useState(null);
    const newSlotErrorTimerRef = SP_REACT.useRef(null);
    const [isOffline, setIsOffline] = SP_REACT.useState(getRommConnectionState() === "offline");
    const [versionHistoryKey, setVersionHistoryKey] = SP_REACT.useState(0);
    const [strandedVersion, setStrandedVersion] = SP_REACT.useState(null);
    const handleVersionRestored = () => {
        setVersionHistoryKey((k) => k + 1);
        globalThis.dispatchEvent(new CustomEvent("romm_data_changed", {
            detail: { type: "save_sync", rom_id: romId },
        }));
    };
    const handleSlotDeleted = () => {
        globalThis.dispatchEvent(new CustomEvent("romm_data_changed", {
            detail: { type: "save_sync", rom_id: romId },
        }));
    };
    SP_REACT.useEffect(() => onRommConnectionChange((s) => setIsOffline(s === "offline")), []);
    SP_REACT.useEffect(() => {
        return () => {
            if (newSlotErrorTimerRef.current)
                clearTimeout(newSlotErrorTimerRef.current);
        };
    }, []);
    SP_REACT.useEffect(() => {
        let cancelled = false;
        const isCancelled = () => cancelled;
        const check = async () => {
            try {
                const list = await getVersionList(appId);
                if (isCancelled())
                    return;
                const inactiveInstalled = list.multi_version
                    ? (list.versions ?? []).filter((v) => v.installed && !v.active && !v.vanished)
                    : [];
                let stranded = null;
                for (const v of inactiveInstalled) {
                    const drift = await checkLocalDrift(v.rom_id);
                    if (isCancelled())
                        return;
                    if (drift.drifted) {
                        stranded = v.label || v.name || String(v.rom_id);
                        break;
                    }
                }
                setStrandedVersion(stranded);
            }
            catch (e) {
                if (!isCancelled())
                    setStrandedVersion(null);
                logWarn(`SavesTab: stranded-version check failed for appId ${appId}: ${e}`);
            }
        };
        detach(check());
        return () => {
            cancelled = true;
        };
    }, [appId, romId]);
    const openCopyModal = useCopyToSlot(romId, availableSlots);
    const offlineBanner = isOffline ? (SP_JSX.jsx("div", { style: {
            padding: "8px",
            background: "rgba(217, 65, 38, 0.15)",
            borderRadius: "4px",
            border: "1px solid rgba(217, 65, 38, 0.4)",
            marginBottom: "12px",
            fontSize: "12px",
            color: "#d94126",
        }, children: "RomM is offline — slot switching is disabled until the server is reachable. This prevents save sync conflicts." }, "offline-banner")) : null;
    const strandedBanner = strandedVersion ? (SP_JSX.jsx("div", { style: {
            padding: "8px",
            background: "rgba(255, 136, 0, 0.15)",
            borderRadius: "4px",
            border: "1px solid rgba(255, 136, 0, 0.3)",
            marginBottom: "12px",
            fontSize: "12px",
            color: "#ff8800",
        }, children: `Version "${strandedVersion}" has saves that were never uploaded — switch back to sync them.` }, "stranded-banner")) : null;
    const legacyWarning = activeSlot === null ? (SP_JSX.jsx("div", { style: {
            padding: "8px",
            background: "rgba(255, 136, 0, 0.15)",
            borderRadius: "4px",
            border: "1px solid rgba(255, 136, 0, 0.3)",
            marginBottom: "12px",
            fontSize: "12px",
            color: "#ff8800",
        }, children: "This game uses legacy mode (no slot). Only one save version per game is supported." }, "legacy-warning")) : null;
    if (slotsLoading) {
        return (SP_JSX.jsxs(DFL.Focusable, { noFocusRing: true, children: [offlineBanner, strandedBanner, SP_JSX.jsx(ConnectingIndicator, {}, "connecting")] }));
    }
    const slotRank = (s) => {
        if (s.slot === activeSlot)
            return 0;
        if (s.slot === "")
            return 2;
        return 1;
    };
    const sorted = [...availableSlots].sort((a, b) => {
        const rankDiff = slotRank(a) - slotRank(b);
        if (rankDiff !== 0)
            return rankDiff;
        return a.slot.localeCompare(b.slot);
    });
    const slotInList = sorted.some((s) => s.slot === activeSlot);
    if (!slotInList && activeSlot && activeSlotKnown) {
        sorted.unshift({ slot: activeSlot, source: "local", count: 0, latest_updated_at: null });
    }
    const handleNewSlot = () => {
        DFL.showModal(SP_JSX.jsx(NewSlotModal, { onSubmit: (name) => {
                if (!name)
                    return;
                detach((async () => {
                    try {
                        const result = await switchSlot(romId, name);
                        if (result.success && result.save_status) {
                            reportServerReachable(true);
                            onSlotSwitched(name, result.save_status);
                        }
                        else {
                            detach(debugLog(`SavesTab: new slot switch failed: ${result.reason}`));
                            let msg = "Failed to create slot";
                            if (result.reason === "pending_uploads") {
                                msg = "Sync your saves first — local changes haven't been uploaded";
                            }
                            else if (result.reason === "server_unreachable") {
                                reportServerReachable(false);
                                msg = "Can't switch — RomM server is not reachable";
                            }
                            setNewSlotError(msg);
                            if (newSlotErrorTimerRef.current)
                                clearTimeout(newSlotErrorTimerRef.current);
                            newSlotErrorTimerRef.current = setTimeout(() => setNewSlotError(null), 5000);
                        }
                    }
                    catch (e) {
                        detach(debugLog(`SavesTab: new slot switch error: ${e}`));
                        setNewSlotError("An error occurred while creating the slot");
                        if (newSlotErrorTimerRef.current)
                            clearTimeout(newSlotErrorTimerRef.current);
                        newSlotErrorTimerRef.current = setTimeout(() => setNewSlotError(null), 5000);
                    }
                })());
            } }));
    };
    const lastKnownSection = !activeSlotKnown && lastKnownSlots ? renderLastKnownSlots(lastKnownSlots) : null;
    let unslottedFilesSection = null;
    if (activeSlot === null || !activeSlotKnown) {
        if (saveStatus && saveStatus.files.length > 0) {
            unslottedFilesSection = (SP_JSX.jsx("div", { style: { marginBottom: "12px" }, children: saveStatus.files.map((f) => {
                    const conflict = conflicts.find((c) => c.filename === f.filename);
                    return renderSaveFileRow(f, conflict, saveStatus.last_sync_check_at);
                }) }, "unslotted-files"));
        }
        else {
            unslottedFilesSection = (SP_JSX.jsx("div", { style: { fontSize: "13px", color: MUTED_COLOR, fontStyle: "italic", marginBottom: "12px" }, children: "No save files tracked yet" }, "no-files"));
        }
    }
    return (SP_JSX.jsxs(DFL.Focusable, { noFocusRing: true, style: { display: "flex", flexDirection: "column", gap: "0" }, children: [offlineBanner, strandedBanner, legacyWarning, unslottedFilesSection, lastKnownSection, sorted
                .filter((s) => activeSlot !== null || s.slot !== "")
                .map((slot) => {
                const isActive = activeSlot !== null && slot.slot === activeSlot;
                return (SP_JSX.jsx(SlotPanel, { romId: romId, slot: slot, isActive: isActive, defaultExpanded: isActive, saveStatus: isActive ? saveStatus : null, conflicts: isActive ? conflicts : [], isOffline: isOffline, onSlotSwitched: onSlotSwitched, onVersionRestored: handleVersionRestored, onSlotDeleted: handleSlotDeleted, onCopy: openCopyModal }, `panel-${slot.slot}-${versionHistoryKey}`));
            }), SP_JSX.jsxs("div", { style: { marginTop: "10px" }, children: [SP_JSX.jsx(DFL.DialogButton, { style: {
                            padding: "6px 12px",
                            minWidth: "auto",
                            fontSize: "12px",
                            width: "auto",
                        }, noFocusRing: false, onFocus: scrollFocusedToCenter, onClick: handleNewSlot, disabled: isOffline, children: "+ New Slot" }, "new-slot-btn"), newSlotError ? (SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#d94126", marginTop: "4px" }, children: newSlotError }, "new-slot-error")) : null] }, "new-slot-area")] }));
};

function formatTimestamp(iso) {
    if (!iso)
        return "";
    try {
        const d = new Date(iso);
        return d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
    }
    catch {
        return iso;
    }
}
const btnStyle = {
    background: "transparent",
    border: "1px solid rgba(255, 255, 255, 0.3)",
    borderRadius: "4px",
    padding: "4px 12px",
    minWidth: "auto",
    width: "auto",
    fontSize: "12px",
    color: "#fff",
    cursor: "pointer",
};
const btnPrimaryStyle = {
    ...btnStyle,
    background: "rgba(26, 159, 255, 0.15)",
    border: "1px solid rgba(26, 159, 255, 0.4)",
    color: "#1a9fff",
};
function getWizardDescription(info) {
    if (!info.has_local_saves && info.server_slots.length > 0) {
        return "Server has saves \u2014 choose which slot to track.";
    }
    if (info.has_local_saves && info.server_slots.length > 0) {
        return "You have local saves and the server has saves too.";
    }
    return "Choose a save slot to get started.";
}
const CustomSlotModal = ({ closeModal, onSubmit }) => {
    const [value, setValue] = SP_REACT.useState("");
    return (SP_JSX.jsx(DFL.ConfirmModal, { ...(closeModal !== undefined ? { closeModal } : {}), strTitle: "Custom Slot Name", bDisableBackgroundDismiss: true, onOK: () => {
            onSubmit(value.trim());
        }, children: SP_JSX.jsx(DFL.TextField, { focusOnMount: true, label: "Slot Name", value: value, onChange: (e) => setValue(e.target.value), onKeyDown: (e) => {
                if (e.key === "Enter" && value.trim() !== "") {
                    onSubmit(value.trim());
                    closeModal?.();
                }
            } }) }));
};
function formatSize(bytes) {
    if (bytes == null || bytes === 0)
        return "unknown";
    return formatBytes$1(bytes);
}
const LegacyMigrationConflictModal = ({ closeModal, conflicts, slot, onConfirm }) => {
    const confirm = () => {
        closeModal?.();
        onConfirm();
    };
    return (SP_JSX.jsx(DFL.ModalRoot, { ...(closeModal !== undefined ? { closeModal } : {}), children: SP_JSX.jsxs("div", { style: { padding: "8px 4px", minWidth: "360px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "15px", fontWeight: "bold", color: "#fff", marginBottom: "4px" }, children: "A local save differs from the legacy save" }), SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.6)", marginBottom: "12px", lineHeight: "1.4" }, children: ["Copying the legacy save into \u2018", slot, "\u2019 replaces your local save."] }), conflicts.map((c) => (SP_JSX.jsxs("div", { style: { marginBottom: "10px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "12px", color: "#fff", marginBottom: "4px" }, children: c.filename }), SP_JSX.jsxs("div", { style: { display: "flex", gap: "8px" }, children: [SP_JSX.jsxs("div", { style: {
                                        flex: 1,
                                        padding: "8px",
                                        background: "rgba(76, 175, 80, 0.15)",
                                        border: "1px solid rgba(76, 175, 80, 0.3)",
                                        borderRadius: "4px",
                                    }, children: [SP_JSX.jsx("div", { style: { fontSize: "11px", fontWeight: "bold", color: "#81c784", marginBottom: "2px" }, children: "Your local save" }), SP_JSX.jsxs("div", { style: { fontSize: "11px", color: "rgba(255, 255, 255, 0.7)" }, children: [formatSize(c.local_size), " \u00B7 modified ", formatTimestamp(c.local_mtime)] })] }), SP_JSX.jsxs("div", { style: {
                                        flex: 1,
                                        padding: "8px",
                                        background: "rgba(33, 150, 243, 0.15)",
                                        border: "1px solid rgba(33, 150, 243, 0.3)",
                                        borderRadius: "4px",
                                    }, children: [SP_JSX.jsx("div", { style: { fontSize: "11px", fontWeight: "bold", color: "#64b5f6", marginBottom: "2px" }, children: "Legacy save on server" }), SP_JSX.jsxs("div", { style: { fontSize: "11px", color: "rgba(255, 255, 255, 0.7)" }, children: [formatSize(c.server_size), " \u00B7 saved ", formatTimestamp(c.server_updated_at)] })] })] })] }, c.filename))), SP_JSX.jsx("div", { style: { fontSize: "11px", color: "rgba(255, 255, 255, 0.5)", margin: "4px 0 12px", lineHeight: "1.4" }, children: legacyConflictReplaceNotice(slot) }), SP_JSX.jsxs("div", { style: { display: "flex", gap: "8px", justifyContent: "flex-end" }, children: [SP_JSX.jsx(DFL.DialogButton, { style: btnStyle, onClick: () => closeModal?.(), onFocus: scrollFocusedToCenter, children: "Cancel" }), SP_JSX.jsx(DFL.DialogButton, { style: btnPrimaryStyle, onClick: confirm, onFocus: scrollFocusedToCenter, children: "Replace local save" })] })] }) }));
};
function createConfirmHandler({ romId, setConfirming, setError, onComplete }) {
    const handleConfirm = async (slot, migrate = false, migrateFrom = null, useServerOnConflict = false) => {
        setConfirming(true);
        setError(null);
        try {
            const result = await confirmSlotChoice(romId, slot, migrate, migrateFrom, useServerOnConflict);
            if (result.needs_conflict_resolution) {
                setConfirming(false);
                DFL.showModal(SP_JSX.jsx(LegacyMigrationConflictModal, { conflicts: result.conflicts ?? [], slot: slot, onConfirm: () => detach(handleConfirm(slot, true, migrateFrom, true)) }));
                return;
            }
            if (!result.success) {
                setError(result.message || "Slot confirmation failed");
                setConfirming(false);
                return;
            }
            if (migrate) {
                const body = wizardMigrationOutcomeToastBody(result.migrated ?? 0, result.failed ?? 0, slot);
                if (body)
                    showToast(body);
            }
            onComplete();
        }
        catch (e) {
            setError(`Failed to confirm slot: ${e}`);
            logError(`SlotSetupWizard confirm failed: ${e}`);
            setConfirming(false);
        }
    };
    return handleConfirm;
}
function buildLocalSavesColumn(info) {
    const children = [
        SP_JSX.jsx("div", { className: "romm-panel-section-title", style: { marginBottom: "8px" }, children: "Local Saves" }, "local-title"),
    ];
    if (info.local_files.length > 0) {
        children.push(SP_JSX.jsx("div", { children: info.local_files.map((f) => (SP_JSX.jsxs("div", { style: { display: "flex", alignItems: "center", gap: "6px", padding: "4px 0", fontSize: "12px" }, children: [SP_JSX.jsx("span", { className: "romm-status-dot", style: { backgroundColor: "#5ba32b" } }), SP_JSX.jsx("span", { style: { color: "#fff" }, children: f.filename }), SP_JSX.jsx("span", { className: "romm-panel-muted", children: formatBytes$1(f.size) })] }, f.filename))) }, "local-files"));
    }
    else {
        children.push(SP_JSX.jsx("div", { className: "romm-panel-muted", style: { fontSize: "12px" }, children: "No local saves found" }, "no-local"));
    }
    return children;
}
function buildSlotRow(s, defaultSlot, handleConfirm) {
    const slotKey = s.slot ?? "__null__";
    const isLegacyGroup = s.slot === null || s.slot === "";
    return (SP_JSX.jsxs("div", { style: {
            padding: "6px 0",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "8px",
        }, children: [SP_JSX.jsxs("div", { style: { minWidth: 0 }, children: [SP_JSX.jsxs("div", { style: { display: "flex", alignItems: "center", gap: "6px", fontSize: "13px", color: "#fff" }, children: [SP_JSX.jsx("span", { className: "romm-status-dot", style: { backgroundColor: "#1a9fff" } }), displaySlot(s.slot)] }), SP_JSX.jsxs("div", { className: "romm-panel-muted", style: { fontSize: "11px", marginLeft: "18px" }, children: [s.count, " file", s.count === 1 ? "" : "s", s.latest_updated_at ? ` — ${formatTimestamp(s.latest_updated_at)}` : ""] }), isLegacyGroup ? (SP_JSX.jsx("div", { className: "romm-panel-muted", style: { fontSize: "11px", marginLeft: "18px", marginTop: "2px" }, children: legacyTrackExplainer(defaultSlot) })) : null] }), SP_JSX.jsx(DFL.DialogButton, { className: "romm-wizard-btn", style: btnStyle, onClick: () => {
                    if (isLegacyGroup) {
                        DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Migrate Legacy Saves?", strDescription: legacyMigrateConfirmDescription(defaultSlot), onOK: () => {
                                detach(handleConfirm(defaultSlot, true, null));
                            } }));
                    }
                    else {
                        detach(handleConfirm(s.slot));
                    }
                }, onFocus: scrollFocusedToCenter, children: "Track" })] }, `slot-${slotKey}`));
}
function buildServerSlotsColumn(info, defaultSlot, handleConfirm) {
    const children = [
        SP_JSX.jsx("div", { className: "romm-panel-section-title", style: { marginBottom: "8px" }, children: "Server Slots" }, "server-title"),
    ];
    if (info.server_slots.length > 0) {
        info.server_slots.forEach((s) => children.push(buildSlotRow(s, defaultSlot, handleConfirm)));
    }
    else {
        children.push(SP_JSX.jsx("div", { className: "romm-panel-muted", style: { fontSize: "12px" }, children: "No saves on server" }, "no-server"));
    }
    const defaultExistsOnServer = info.server_slots.some((s) => s.slot === defaultSlot);
    children.push(SP_JSX.jsx("div", { style: { borderTop: "1px solid rgba(255, 255, 255, 0.1)", margin: "10px 0 8px" } }, "divider"));
    if (!defaultExistsOnServer) {
        children.push(SP_JSX.jsx("div", { className: "romm-panel-muted", style: { fontSize: "11px", marginBottom: "6px" }, children: "Or start fresh:" }, "fresh-label"), SP_JSX.jsx("div", { style: { marginBottom: "6px" }, children: SP_JSX.jsxs(DFL.DialogButton, { className: "romm-wizard-btn romm-wizard-btn-primary", style: btnPrimaryStyle, onClick: () => {
                    detach(handleConfirm(defaultSlot));
                }, onFocus: scrollFocusedToCenter, children: ["Use slot \u2018", defaultSlot, "\u2019"] }) }, "default-btn"));
        if (info.has_local_saves) {
            children.push(SP_JSX.jsx("div", { className: "romm-panel-muted", style: { fontSize: "11px", marginBottom: "6px" }, children: startFreshHint(defaultSlot) }, "fresh-hint"));
        }
    }
    children.push(SP_JSX.jsx("div", { children: SP_JSX.jsx(DFL.DialogButton, { className: "romm-wizard-btn", style: btnStyle, onFocus: scrollFocusedToCenter, onClick: () => {
                DFL.showModal(SP_JSX.jsx(CustomSlotModal, { onSubmit: (trimmed) => {
                        detach(handleConfirm(trimmed));
                    } }));
            }, children: "Custom slot..." }) }, "custom-toggle"));
    if (info.has_local_saves && defaultExistsOnServer) {
        children.push(SP_JSX.jsx("div", { className: "romm-panel-muted", style: { fontSize: "11px", marginTop: "6px" }, children: startFreshHintNewSlot() }, "custom-fresh-hint"));
    }
    return children;
}
function useSaveSetupInfo(romId, onComplete) {
    const [info, setInfo] = SP_REACT.useState(null);
    const [loading, setLoading] = SP_REACT.useState(true);
    const [confirming, setConfirming] = SP_REACT.useState(false);
    const [error, setError] = SP_REACT.useState(null);
    const [reloadKey, setReloadKey] = SP_REACT.useState(0);
    const offlineHeldRef = SP_REACT.useRef(false);
    SP_REACT.useEffect(() => {
        let cancelled = false;
        const fetchInfo = async () => {
            if (getRommConnectionState() === "offline") {
                offlineHeldRef.current = true;
                if (!cancelled) {
                    setError(SERVER_UNREACHABLE_WIZARD_MESSAGE);
                    setLoading(false);
                }
                return;
            }
            const load = beginServerLoad();
            setServerRetryProgress(null);
            setLoading(true);
            setError(null);
            try {
                const result = await getSaveSetupInfo(romId);
                if (cancelled)
                    return;
                const reachable = result.recommended_action !== "server_unreachable";
                reportServerReachable(reachable);
                offlineHeldRef.current = !reachable;
                await applyWizardInitialSetupResult(result, {
                    romId,
                    confirmSlotChoice,
                    setError,
                    setConfirming,
                    setInfo,
                    logError,
                    onComplete,
                    isCancelled: () => cancelled,
                });
            }
            catch (e) {
                if (!cancelled) {
                    setError(`Failed to load save setup info: ${e}`);
                    logError(`SlotSetupWizard fetch failed: ${e}`);
                }
            }
            finally {
                settleServerLoad(load);
                if (!cancelled)
                    setLoading(false);
            }
        };
        detach(fetchInfo());
        return () => {
            cancelled = true;
        };
    }, [romId, reloadKey]);
    SP_REACT.useEffect(() => onRommConnectionChange((s) => {
        if (s === "connected" && offlineHeldRef.current) {
            offlineHeldRef.current = false;
            setReloadKey((k) => k + 1);
        }
    }), []);
    const retry = () => {
        setError(null);
        setLoading(true);
        const load = beginServerLoad();
        setServerRetryProgress(null);
        getSaveSetupInfo(romId)
            .then((result) => {
            const reachable = result.recommended_action !== "server_unreachable";
            reportServerReachable(reachable);
            offlineHeldRef.current = !reachable;
            applyWizardRetrySetupResult(result, { setError, setLoading, setInfo });
        }, (e) => {
            setError(`Failed: ${e}`);
            setLoading(false);
        })
            .finally(() => settleServerLoad(load));
    };
    return { info, loading, confirming, error, setConfirming, setError, retry };
}
const SlotSetupWizard = ({ romId, onComplete }) => {
    const { info, loading, confirming, error, setConfirming, setError, retry } = useSaveSetupInfo(romId, onComplete);
    const handleConfirm = createConfirmHandler({ romId, setConfirming, setError, onComplete });
    if (loading || (confirming && !error)) {
        return (SP_JSX.jsxs("div", { style: { padding: "12px 0" }, children: [SP_JSX.jsx("div", { className: "romm-panel-section-title", children: "Save Slot Setup" }), SP_JSX.jsx(ConnectingIndicator, { label: confirming ? "Setting up" : "Connecting to RomM" })] }));
    }
    if (error && !info) {
        return (SP_JSX.jsxs("div", { style: { padding: "12px 0" }, children: [SP_JSX.jsx("div", { className: "romm-panel-section-title", children: "Save Slot Setup" }), SP_JSX.jsx("div", { style: { color: "#d4513f", fontSize: "12px", marginBottom: "8px" }, children: error }), SP_JSX.jsx(DFL.DialogButton, { className: "romm-wizard-btn", style: btnStyle, onClick: retry, children: "Retry" })] }));
    }
    if (!info)
        return null;
    const defaultSlot = info.default_slot;
    const leftChildren = buildLocalSavesColumn(info);
    const rightChildren = buildServerSlotsColumn(info, defaultSlot, handleConfirm);
    return (SP_JSX.jsxs("div", { style: { padding: "12px 0" }, children: [SP_JSX.jsx("div", { className: "romm-panel-section-title", style: { marginBottom: "4px" }, children: "Save Slot Setup" }), error && SP_JSX.jsx("div", { style: { color: "#d4513f", fontSize: "12px", marginBottom: "8px" }, children: error }), SP_JSX.jsx("div", { className: "romm-panel-muted", style: { fontSize: "12px", marginBottom: "12px" }, children: getWizardDescription(info) }), SP_JSX.jsxs("div", { style: { display: "flex", gap: "24px" }, children: [SP_JSX.jsx("div", { style: { flex: 2, minWidth: 0 }, children: leftChildren }), SP_JSX.jsx("div", { style: { flex: 1, minWidth: 0 }, children: rightChildren })] })] }));
};

function announceSaveSyncChange(romId) {
    globalThis.dispatchEvent(new CustomEvent("romm_data_changed", {
        detail: { type: "save_sync", rom_id: romId },
    }));
}
function buildTabContent({ appId, binding, state }) {
    const romId = binding.romId;
    if (state.activeTab === "info") {
        return (SP_JSX.jsx(GameInfoTab, { romName: state.romName, regions: state.regions, languages: state.languages, metadata: state.metadata, platformName: state.platformName, coverBase64: state.coverBase64, installed: state.installed, installedRom: state.installedRom }, "tab-info"));
    }
    if (state.activeTab !== "saves")
        return null;
    if (state.saveSyncEnabled && !state.slotConfirmed) {
        return (SP_JSX.jsx(SlotSetupWizard, { romId: romId, onComplete: () => {
                binding.write((prev) => ({ ...prev, slotConfirmed: true }));
                announceSaveSyncChange(romId);
            } }));
    }
    return (SP_JSX.jsx(SavesTab, { appId: appId, romId: romId, saveStatus: state.saveStatus, conflicts: state.conflicts, activeSlot: state.activeSlot, activeSlotKnown: state.activeSlotKnown, availableSlots: state.availableSlots, lastKnownSlots: state.lastKnownSlots, slotsLoading: state.slotsLoading, onSlotSwitched: (newSlot, newStatus) => {
            binding.write((prev) => ({
                ...prev,
                activeSlot: newSlot === "" ? null : newSlot,
                activeSlotKnown: true,
                saveStatus: newStatus,
                conflicts: newStatus.conflicts ?? [],
            }));
            announceSaveSyncChange(romId);
        } }));
}

const MigrationBlockedCard = ({ compact = false }) => (SP_JSX.jsx(WarningCard, { title: "RetroDECK Migration Required", message: "Open the plugin QAM to migrate files or dismiss the migration before playing.", compact: compact }));

const SETTINGS_RESET_TITLE = "Settings were reset";
function settingsResetMessage(backedUpTo) {
    const backup = backedUpTo
        ? `A backup of your old settings was saved to ${backedUpTo}.`
        : "A backup of your old settings was saved.";
    return `Your settings file was corrupt and has been reset. Re-enter your server URL and sign in again. ${backup}`;
}
function settingsResetCardMessage(backedUpTo) {
    const backup = backedUpTo
        ? `A backup of your old settings was saved to ${backedUpTo}.`
        : "A backup of your old settings was saved.";
    return `Your settings file was corrupt and has been reset. Re-enter your server URL and sign in again. ${backup} Open the Arcoon Deck menu (QAM) to dismiss this.`;
}
const SettingsResetBanner = ({ backedUpTo }) => {
    const handleDismiss = () => {
        detach(dismissSettingsResetNotice().then(() => setSettingsResetState({ pending: false, backedUpTo: null }), (e) => logError(`Failed to dismiss settings reset notice: ${e}`)));
    };
    return (SP_JSX.jsxs(DFL.PanelSection, { title: SETTINGS_RESET_TITLE, children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs("div", { style: {
                        padding: "8px 12px",
                        backgroundColor: "rgba(212, 167, 44, 0.15)",
                        borderLeft: "3px solid #d4a72c",
                        borderRadius: "4px",
                    }, children: [SP_JSX.jsxs("div", { style: {
                                fontSize: "13px",
                                fontWeight: "bold",
                                color: "#d4a72c",
                                marginBottom: "6px",
                            }, children: ["⚠️", " ", SETTINGS_RESET_TITLE] }), SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.85)", lineHeight: 1.5 }, children: settingsResetMessage(backedUpTo) })] }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: handleDismiss, children: "Dismiss" }) })] }));
};

const SettingsResetCard = ({ backedUpTo, compact = false }) => (SP_JSX.jsx(WarningCard, { title: SETTINGS_RESET_TITLE, message: settingsResetCardMessage(backedUpTo), compact: compact }));

const RomMGameInfoPanel = ({ appId }) => {
    const versionError = useVersionError();
    const [state, setState] = SP_REACT.useState({
        loading: true,
        romId: null,
        romName: "",
        platformName: "",
        installed: false,
        installedRom: null,
        metadata: null,
        coverBase64: null,
        biosStatus: null,
        biosLevel: null,
        coreInfo: null,
        saveSyncEnabled: false,
        saveStatus: null,
        conflicts: [],
        error: false,
        activeTab: "info",
        raId: null,
        slotConfirmed: false,
        activeSlot: "default",
        activeSlotKnown: false,
        availableSlots: [],
        lastKnownSlots: null,
        slotsLoading: false,
        regions: [],
        languages: [],
    });
    const romIdRef = SP_REACT.useRef(null);
    const platformSlugRef = SP_REACT.useRef("");
    const slotsLoadedRef = SP_REACT.useRef(false);
    const readSeqs = SP_REACT.useRef({ detail: 0, saveStatus: 0, slots: 0, slotTracking: 0, bios: 0 });
    const migration = useMigrationStatus();
    const settingsReset = useSettingsResetState();
    const saveSortPending = useSaveSortMigrationState().pending;
    SP_REACT.useEffect(() => {
        refreshMigrationState()
            .then(({ retrodeck, save_sort }) => {
            setMigrationStatus(retrodeck);
            setSaveSortMigrationStatus(save_sort);
        })
            .catch((e) => logError(`Failed to refresh migration state: ${e}`));
    }, [appId]);
    SP_REACT.useEffect(() => {
        let cancelled = false;
        detach(loadData(appId, () => cancelled, romIdRef, platformSlugRef, readSeqs, setState));
        const unwire = wirePanelEvents({
            appId,
            cancelled: () => cancelled,
            romIdRef,
            platformSlugRef,
            slotsLoadedRef,
            readSeqs,
            setState,
        });
        return () => {
            cancelled = true;
            unwire();
        };
    }, [appId]);
    useSaveSlotsLoad(state, slotsLoadedRef, readSeqs, setState);
    if (versionError) {
        return (SP_JSX.jsx("div", { "data-romm": "true", children: SP_JSX.jsx(VersionErrorCard, { message: versionError }) }));
    }
    if (settingsReset.pending) {
        return (SP_JSX.jsx("div", { "data-romm": "true", children: SP_JSX.jsx(SettingsResetCard, { backedUpTo: settingsReset.backedUpTo, compact: true }) }));
    }
    if (migration.pending) {
        return (SP_JSX.jsx("div", { "data-romm": "true", children: SP_JSX.jsx(MigrationBlockedCard, {}) }));
    }
    if (state.loading) {
        return (SP_JSX.jsx("div", { "data-romm": "true", className: "romm-panel-container", style: { minHeight: "500px" }, children: SP_JSX.jsx("div", { className: "romm-panel-loading", children: "Loading..." }) }));
    }
    if (state.error || !state.romId) {
        return null;
    }
    const romId = state.romId;
    return (SP_JSX.jsxs("div", { "data-romm": "true", children: [saveSortPending ? SP_JSX.jsx(SaveSortWarning, {}, "save-sort-warning") : null, SP_JSX.jsx(PanelTabBar, { activeTab: state.activeTab, hasAchievements: !!state.raId, hasSaves: state.saveSyncEnabled, hasBios: !!state.biosStatus, onSelect: (tabId) => setState((prev) => ({ ...prev, activeTab: tabId })) }), SP_JSX.jsxs(DFL.Focusable, { noFocusRing: true, className: "romm-tab-content", style: { paddingBottom: "48px" }, children: [buildTabContent({ appId, binding: bindRomInState(romId, setState), state }), SP_JSX.jsx(AchievementsTab, { romId: romId, raId: state.raId, isActive: state.activeTab === "achievements" }, `achievements-${romId}`), SP_JSX.jsx(BiosTab, { biosStatus: state.biosStatus, biosLevel: state.biosLevel, coreInfo: state.coreInfo, isActive: state.activeTab === "bios" })] })] }));
};

const rommAppIds = new Set();
let treeDumped = false;
function resolveTypeName(node) {
    if (typeof node?.type === "string")
        return node.type;
    if (typeof node?.type === "function")
        return "(anonymous fn)";
    return String(node?.type ?? "null");
}
function deepTreeDump(node, depth, index, prefix) {
    if (depth > 5)
        return;
    if (node == null || typeof node !== "object")
        return;
    const indent = "  ".repeat(depth);
    const typeName = node?.type?.name || node?.type?.displayName || resolveTypeName(node);
    const key = node?.key ?? "null";
    const className = (node?.props?.className || "").substring(0, 60) || "(none)";
    const childrenRaw = node?.props?.children;
    let childCount;
    if (Array.isArray(childrenRaw)) {
        childCount = childrenRaw.length;
    }
    else if (childrenRaw == null) {
        childCount = 0;
    }
    else {
        childCount = 1;
    }
    detach(debugLog(`${prefix}${indent}[${depth}:${index}] type=${typeName} key=${key} cls=${className} children=${childCount}`));
    if (Array.isArray(childrenRaw)) {
        for (let i = 0; i < childrenRaw.length; i++) {
            deepTreeDump(childrenRaw[i], depth + 1, i, prefix);
        }
    }
    else if (childrenRaw != null && typeof childrenRaw === "object") {
        deepTreeDump(childrenRaw, depth + 1, 0, prefix);
    }
}
function findInsertionPoint(ret) {
    const innerContainerClass = appDetailsClasses?.InnerContainer;
    if (!innerContainerClass)
        return undefined;
    return DFL.findInReactTree(ret, (x) => Array.isArray(x?.props?.children) && x?.props?.className?.includes(innerContainerClass));
}
function findNativeOverviewIndex(children) {
    for (let i = 0; i < children.length; i++) {
        const cp = children[i]?.props?.children?.props || {};
        if (cp.details && cp.overview && cp.bFastRender !== undefined) {
            return i;
        }
    }
    return -1;
}
function dumpTree(container, appId) {
    if (!rommAppIds.has(appId) || treeDumped)
        return;
    treeDumped = true;
    detach(debugLog(`===== DEEP TREE DUMP for appId=${appId} =====`));
    detach(debugLog(`InnerContainer className: ${container.props.className}`));
    const children = container.props.children;
    detach(debugLog(`InnerContainer direct children count: ${children.length}`));
    for (let i = 0; i < children.length; i++) {
        deepTreeDump(children[i], 0, i, "TREE: ");
    }
    const psContainerClass = playSectionClasses?.Container;
    detach(debugLog(`playSectionClasses.Container = "${psContainerClass || "UNDEFINED"}"`));
    if (psContainerClass) {
        const psFound = DFL.findInReactTree(container, (x) => x?.props?.className?.includes?.(psContainerClass));
        detach(debugLog(`findInReactTree(playSectionClasses.Container): ${psFound ? "FOUND" : "NOT FOUND"}`));
    }
    const bpsClass = basicAppDetailsSectionStylerClasses?.PlaySection;
    detach(debugLog(`basicAppDetailsSectionStylerClasses.PlaySection = "${bpsClass || "UNDEFINED"}"`));
    if (bpsClass) {
        const bpsFound = DFL.findInReactTree(container, (x) => x?.props?.className?.includes?.(bpsClass));
        detach(debugLog(`findInReactTree(basicAppDetailsSectionStylerClasses.PlaySection): ${bpsFound ? "FOUND" : "NOT FOUND"}`));
    }
    detach(debugLog(`===== END DEEP TREE DUMP =====`));
}
function registerRomMAppId(appId) {
    rommAppIds.add(appId);
}
function unregisterRomMAppId(appId) {
    rommAppIds.delete(appId);
}
function isRomMAppId(appId) {
    return rommAppIds.has(appId);
}
let gamePatch = null;
function registerGameDetailPatch() {
    gamePatch = routerHook.addPatch("/library/app/:appid", (tree) => {
        const routeProps = DFL.findInReactTree(tree, (x) => x?.renderFunc);
        if (routeProps) {
            const patchHandler = DFL.createReactTreePatcher([
                (node) => DFL.findInReactTree(node, (x) => x?.props?.children?.props?.overview)?.props?.children,
            ], (_args, ret) => {
                const container = findInsertionPoint(ret);
                if (typeof container !== "object" || !container) {
                    return ret;
                }
                const overviewNode = DFL.findInReactTree(ret, (x) => x?.props?.overview?.appid);
                const appId = overviewNode?.props?.overview?.appid;
                if (!appId) {
                    return ret;
                }
                const isRomM = rommAppIds.has(appId);
                detach(debugLog(`gameDetailPatch: appId=${appId} isRomM=${isRomM} setSize=${rommAppIds.size}`));
                dumpTree(container, appId);
                if (isRomM) {
                    const children = container.props.children;
                    const alreadyHasPlayBtn = children.some((c) => c?.key === "romm-play-section");
                    if (!alreadyHasPlayBtn) {
                        const nativeOverviewIdx = findNativeOverviewIndex(children);
                        const rommPlaySection = SP_JSX.jsx(RomMPlaySection, { appId: appId }, "romm-play-section");
                        const rommInfoPanel = SP_JSX.jsx(RomMGameInfoPanel, { appId: appId }, "romm-info-panel");
                        const rommWrapper = (SP_JSX.jsxs("div", { className: appDetailsClasses?.AppDetailsOverviewPanel || "", "data-romm": "true", children: [rommPlaySection, rommInfoPanel] }, "romm-play-section"));
                        if (nativeOverviewIdx >= 0) {
                            detach(debugLog(`gameDetailPatch: replacing AppDetailsOverviewPanel at index ${nativeOverviewIdx} with RomM wrapper (cls=${appDetailsClasses?.AppDetailsOverviewPanel})`));
                            children.splice(nativeOverviewIdx, 1, rommWrapper);
                        }
                        else {
                            detach(debugLog(`gameDetailPatch: AppDetailsOverviewPanel not found, inserting RomM wrapper at index 1`));
                            children.splice(1, 0, rommWrapper);
                        }
                    }
                }
                return ret;
            }, "RomMGameDetail");
            DFL.afterPatch(routeProps, "renderFunc", patchHandler);
        }
        return tree;
    });
}
function unregisterGameDetailPatch() {
    if (gamePatch) {
        routerHook.removePatch("/library/app/:appid", gamePatch);
        gamePatch = null;
    }
}

let _cancelRequested = false;
let _isUnitRunning = false;
let _scanCache = null;
let _orphanPoolCache = null;
function requestSyncCancel() {
    _cancelRequested = true;
}
function resetSyncCancel() {
    _cancelRequested = false;
}
function isCancelRequested() {
    return _cancelRequested;
}
function buildAdoptableOrphanPool(liveAppIds, boundMap) {
    const pool = new Map();
    if (liveAppIds === null) {
        logInfo("orphan adoption: live shortcut store unreadable; adoption disabled for this run");
        return pool;
    }
    if (typeof appStore === "undefined") {
        logInfo("orphan adoption: appStore unavailable; adoption disabled for this run");
        return pool;
    }
    const boundAppIds = new Set(boundMap.values());
    let orphanCount = 0;
    for (const appId of liveAppIds) {
        if (boundAppIds.has(appId))
            continue;
        const overview = appStore.GetAppOverviewByAppID(appId);
        const name = overview?.strDisplayName || overview?.display_name;
        if (!name)
            continue;
        const bucket = pool.get(name);
        if (bucket)
            bucket.push(appId);
        else
            pool.set(name, [appId]);
        orphanCount++;
    }
    for (const bucket of pool.values())
        bucket.sort((a, b) => a - b);
    logInfo(`orphan adoption: pool holds ${orphanCount} adoptable orphan(s) across ${pool.size} name(s)`);
    return pool;
}
function resolveAdoptableOrphanPool(runId, liveAppIds, boundMap) {
    if (_orphanPoolCache?.runId === runId)
        return _orphanPoolCache.pool;
    const pool = buildAdoptableOrphanPool(liveAppIds, boundMap);
    _orphanPoolCache = { runId, pool };
    return pool;
}
function takeAdoptableOrphan(pool, name) {
    const bucket = pool.get(name);
    if (!bucket || bucket.length === 0)
        return undefined;
    return bucket.shift();
}
async function rewriteShortcutIdentity(appId, item) {
    SteamClient.Apps.SetShortcutName(appId, item.name);
    SteamClient.Apps.SetShortcutExe(appId, item.exe);
    SteamClient.Apps.SetShortcutStartDir(appId, item.start_dir);
    await setLaunchOptionsConfirmed(appId, item.launch_options);
}
async function resolveShortcutAppId(item, existing, runId, liveAppIds) {
    const existingAppId = existing.get(item.rom_id);
    if (existingAppId) {
        await rewriteShortcutIdentity(existingAppId, item);
        return { appId: existingAppId, created: false };
    }
    const orphanPool = resolveAdoptableOrphanPool(runId, liveAppIds, existing);
    const adoptedAppId = takeAdoptableOrphan(orphanPool, item.name);
    if (adoptedAppId !== undefined) {
        await rewriteShortcutIdentity(adoptedAppId, item);
        recordSyncCreated(adoptedAppId);
        logInfo(`adopted orphan shortcut ${adoptedAppId} for rom ${item.rom_id} (${item.name})`);
        return { appId: adoptedAppId, created: true };
    }
    const createdAppId = (await addShortcut(item)) ?? undefined;
    if (createdAppId)
        recordSyncCreated(createdAppId);
    return { appId: createdAppId, created: createdAppId !== undefined };
}
async function applyCoverArtwork(appId, romId) {
    try {
        const { base64 } = await getArtworkBase64(romId);
        if (base64) {
            await SteamClient.Apps.SetCustomArtworkForApp(appId, base64, "png", 0);
        }
    }
    catch (e) {
        logError(`Per-unit: failed to apply cover for rom ${romId} (appId ${appId}): ${e}`);
    }
}
async function processCoverRefreshes(data) {
    const refreshes = data.cover_refreshes ?? [];
    const total = refreshes.length;
    const showCoverProgress = (done) => {
        updateSyncProgress({
            running: true,
            stage: "applying",
            message: `${data.unit_name}: covers ${done}/${total}`,
            step: data.unit_index + 1,
            totalSteps: data.total_units,
            runId: data.run_id,
            coverRefresh: true,
        });
    };
    showCoverProgress(0);
    const completed = await pacedForEach(refreshes, (entry) => applyCoverArtwork(entry.app_id, entry.rom_id), {
        heartbeat: () => {
            syncHeartbeat().catch(() => { });
        },
        isCancelled: isCancelRequested,
        onProgress: showCoverProgress,
    });
    if (!completed)
        logInfo("Per-unit cancel observed during cover refresh");
}
async function processUnitShortcuts(data, existing, liveAppIds, romIdToAppId) {
    const completed = await pacedForEach(data.shortcuts, async (item, i) => {
        const unitCurrent = data.chunk_offset + i + 1;
        try {
            updateSyncProgress({
                running: true,
                stage: "applying",
                current: unitCurrent,
                total: data.unit_total,
                message: `${data.unit_name}: ${unitCurrent}/${data.unit_total}`,
                step: data.unit_index + 1,
                totalSteps: data.total_units,
                runId: data.run_id,
            });
            const { appId, created } = await resolveShortcutAppId(item, existing, data.run_id, liveAppIds);
            if (appId) {
                romIdToAppId[String(item.rom_id)] = appId;
                if (created)
                    recordUnitCreated(data.unit_index);
                else
                    recordUnitUpdated(data.unit_index);
                registerRomMAppId(appId);
                if (created)
                    await applyCoverArtwork(appId, item.rom_id);
            }
        }
        catch (e) {
            logError(`Per-unit: failed to process shortcut for rom ${item.rom_id}: ${e}`);
        }
    }, {
        heartbeat: () => {
            syncHeartbeat().catch(() => { });
        },
        isCancelled: isCancelRequested,
    });
    if (!completed)
        logInfo(`Per-unit cancel observed during ${data.unit_name}`);
}
async function resolveExistingShortcuts(runId) {
    if (_scanCache?.runId === runId)
        return { map: _scanCache.map, liveAppIds: _scanCache.liveAppIds };
    const start = Date.now();
    const liveAppIds = (await getLiveRomMShortcutAppIds()) ?? null;
    const map = await getExistingRomMShortcuts(liveAppIds);
    _scanCache = { runId, map, liveAppIds };
    logInfo(`getExistingRomMShortcuts: scanned ${map.size} RomM shortcuts in ${Date.now() - start}ms (run ${runId})`);
    return { map, liveAppIds };
}
async function reconcileStaleShortcuts() {
    let liveAppIds;
    try {
        liveAppIds = await getLiveRomMShortcutAppIds();
    }
    catch (e) {
        logError(`reconcileStaleShortcuts: failed to scan live shortcuts: ${e}`);
        return;
    }
    if (liveAppIds === null)
        return;
    try {
        const result = await reconcileShortcuts(liveAppIds);
        if (result.unbound_count) {
            logInfo(`reconcileStaleShortcuts: backend unbound ${result.unbound_count} stale shortcut(s)`);
        }
    }
    catch (e) {
        logError(`reconcileStaleShortcuts: backend reconcile failed: ${e}`);
    }
}
function initUnitSyncManager() {
    return addEventListener("sync_apply_unit", async (data) => {
        if (_isUnitRunning) {
            logInfo(`sync_apply_unit: already processing a unit, dropping duplicate for ${data.unit_name}`);
            return;
        }
        _isUnitRunning = true;
        try {
            if (!Array.isArray(data.shortcuts)) {
                logError("sync_apply_unit: data.shortcuts is not an array, aborting");
                return;
            }
            _cancelRequested = false;
            const romIdToAppId = {};
            observeUnitTotal(data.unit_index, data.unit_total);
            const total = data.shortcuts.length;
            logInfo(`sync_apply_unit received: ${data.unit_type}=${data.unit_name} (${data.unit_index + 1}/${data.total_units}), ` +
                `chunk ${data.chunk_index + 1}/${data.chunk_count}, ${total} shortcuts`);
            updateSyncProgress({
                running: true,
                stage: "applying",
                current: data.chunk_offset,
                total: data.unit_total,
                message: `${data.unit_name}: ${data.chunk_offset}/${data.unit_total}`,
                step: data.unit_index + 1,
                totalSteps: data.total_units,
                runId: data.run_id,
                coverRefresh: false,
            });
            const { map: existing, liveAppIds } = await resolveExistingShortcuts(data.run_id);
            await processUnitShortcuts(data, existing, liveAppIds, romIdToAppId);
            if (!isCancelRequested() && data.cover_refreshes?.length) {
                await processCoverRefreshes(data);
            }
            if (isCancelRequested()) {
                logInfo(`Per-unit cancel observed for ${data.unit_name}; skipping reportUnitResults`);
            }
            else {
                try {
                    await reportUnitResults(romIdToAppId, data.run_id, data.unit_id, data.chunk_index);
                }
                catch (e) {
                    logError(`Failed to report unit results for ${data.unit_name}: ${e}`);
                }
            }
            logInfo(`sync_apply_unit complete: ${data.unit_name} chunk ${data.chunk_index + 1}/${data.chunk_count} ` +
                `(${Object.keys(romIdToAppId).length}/${total})`);
        }
        finally {
            _isUnitRunning = false;
        }
    });
}

const CONNECTION_RETRY_DELAYS = [2000, 5000, 10000, 15000, 20000];
const CONNECTION_CALLABLE_TIMEOUT = 5000;
let _state$1 = { connected: null, failure: null };
let _running = false;
const listeners = new Set();
function publish(next) {
    _state$1 = next;
    listeners.forEach((l) => l(next));
}
function getConnectionProbeState() {
    return _state$1;
}
function onConnectionProbeChange(cb) {
    listeners.add(cb);
    return () => {
        listeners.delete(cb);
    };
}
async function runProbe() {
    for (let attempt = 0;; attempt++) {
        try {
            const r = await withTimeout(testConnection(), CONNECTION_CALLABLE_TIMEOUT);
            publish({ connected: r.success, failure: r.success ? null : { reason: r.reason, message: r.message } });
            setVersionError(r.reason === "version_error" ? r.message : null);
            return;
        }
        catch {
            if (attempt >= CONNECTION_RETRY_DELAYS.length) {
                try {
                    await withTimeout(getSettings(), CONNECTION_CALLABLE_TIMEOUT);
                    publish({ connected: false, failure: null });
                }
                catch (pingErr) {
                    publish({ connected: "backend_failed", failure: null });
                    console.error("[RomM] backend RPC bridge unreachable (get_settings ping failed):", pingErr);
                }
                return;
            }
            await new Promise((resolve) => setTimeout(resolve, CONNECTION_RETRY_DELAYS[attempt]));
        }
    }
}
function ensureConnectionProbe() {
    if (_running)
        return;
    _running = true;
    detach(runProbe().finally(() => {
        _running = false;
    }));
}
function useConnectionProbe() {
    const [state, setState] = SP_REACT.useState(getConnectionProbeState());
    SP_REACT.useEffect(() => {
        const unsubscribe = onConnectionProbeChange(setState);
        ensureConnectionProbe();
        return unsubscribe;
    }, []);
    return state;
}

function retroDeckBanner(status, paths) {
    switch (status) {
        case "unreadable":
            return {
                title: "RetroDECK configuration unreadable",
                message: "Couldn't read RetroDECK's configuration — syncs and downloads may target the wrong location. " +
                    "Check that RetroDECK is installed correctly. " +
                    `Looked at: ${paths.config_path}`,
            };
        case "root_missing":
            return {
                title: "RetroDECK library not found",
                message: "RetroDECK's library folder doesn't exist on disk — if it's on an SD card, make sure the card is inserted. " +
                    `Expected at: ${paths.resolved_home}`,
            };
        default:
            return null;
    }
}

const wrapText = {
    whiteSpace: "normal",
    overflowWrap: "break-word",
    minWidth: 0,
    fontSize: "12px",
};

const DownloadProgressRow = ({ caption, bytesDownloaded, totalBytes }) => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs("div", { style: { width: "100%" }, children: [SP_JSX.jsxs("div", { style: {
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                    fontSize: "12px",
                    marginBottom: "4px",
                }, children: [SP_JSX.jsx("span", { "data-testid": "dl-caption", style: wrapText, children: caption }), SP_JSX.jsx("span", { "data-testid": "dl-bytes", style: { flexShrink: 0 }, children: totalBytes > 0
                            ? `${formatBytes$1(bytesDownloaded)} / ${formatBytes$1(totalBytes)}`
                            : formatBytes$1(bytesDownloaded) })] }), SP_JSX.jsx(DFL.ProgressBar, { indeterminate: totalBytes === 0, ...(totalBytes > 0 ? { nProgress: (bytesDownloaded / totalBytes) * 100 } : {}) })] }) }));

const IDLE = { pending: false, kind: null, message: null };
let _state = IDLE;
let _listeners = [];
function setDataLocationState(state) {
    _state = state;
    _listeners.forEach((fn) => fn());
}
function getDataLocationState() {
    return _state;
}
function onDataLocationChange(fn) {
    _listeners.push(fn);
    return () => {
        _listeners = _listeners.filter((l) => l !== fn);
    };
}
function useDataLocationState() {
    return SP_REACT.useSyncExternalStore(onDataLocationChange, getDataLocationState);
}
async function fetchDataLocationState() {
    const notice = await getDataLocationNotice();
    const next = {
        pending: notice.pending,
        kind: notice.kind,
        message: notice.message,
    };
    setDataLocationState(next);
    return next;
}

function canRestartDevice() {
    return typeof SteamClient.System.RestartPC === "function";
}
function restartSteam() {
    if (isAnyAppRunning()) {
        showToast("Close your running game before restarting Steam.");
        return;
    }
    SteamClient.User.StartRestart(false);
}
function restartDevice() {
    if (isAnyAppRunning()) {
        showToast("Close your running game before restarting.");
        return;
    }
    SteamClient.System.RestartPC?.();
}

const DATA_LOCATION_MODAL_TITLE = "Which copy of your library should Arcoon Deck keep?";
const DATA_LOCATION_CHOSEN_BODY = "Arcoon Deck copies the library you choose the next time it starts. Restarting your Steam Deck is the surest way to get " +
    "there. Nothing changes until then — Arcoon Deck keeps using the copy it started with, and you can pick the other one " +
    "any time before you restart.";
const RESTART_CONFIRM_DESCRIPTION = "This closes your games and reboots the device. Arcoon Deck copies the library you picked while it starts back up.";
function confirmRestartDevice() {
    DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Restart your Steam Deck?", strDescription: RESTART_CONFIRM_DESCRIPTION, strOKButtonText: "Restart now", strCancelButtonText: "Cancel", onOK: restartDevice }));
}
function candidateDetail(candidate) {
    if (!candidate.present)
        return "no longer on disk";
    if (candidate.size_bytes == null)
        return "size could not be measured";
    return `${formatBytes$1(candidate.size_bytes)} · last changed ${formatTimestampWithYear(candidate.changed_at)}`;
}
const DataLocationModal = ({ candidates, chosen, onChoose, onClose, isLoading = false, errorMessage = null, }) => {
    const gameRunning = isAnyAppRunning();
    const rebootable = canRestartDevice();
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: isLoading ? undefined : onClose, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "360px" }, "data-testid": "data-location-modal", children: [SP_JSX.jsx("div", { style: { fontSize: "16px", fontWeight: "bold", marginBottom: "4px", color: "#fff" }, children: DATA_LOCATION_MODAL_TITLE }), SP_JSX.jsx("div", { style: {
                        fontSize: "12px",
                        color: "rgba(255, 255, 255, 0.6)",
                        marginBottom: "16px",
                        lineHeight: "1.4",
                    }, children: chosen === null
                        ? "Two older installs of this plugin both hold a library, so Arcoon Deck has not moved anything. Pick the one " +
                            "to keep. Nothing is deleted — the other stays on disk exactly as it is."
                        : DATA_LOCATION_CHOSEN_BODY }), chosen === null && candidates === null ? (SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "12px" }, children: "Measuring both copies\u2026" })) : null, chosen === null
                    ? (candidates ?? []).map((candidate) => (SP_JSX.jsxs("div", { "data-testid": `data-location-candidate-${candidate.source}`, style: {
                            padding: "10px",
                            background: "rgba(33, 150, 243, 0.15)",
                            borderRadius: "4px",
                            border: "1px solid rgba(33, 150, 243, 0.3)",
                            marginBottom: "10px",
                            opacity: candidate.present ? 1 : 0.6,
                        }, children: [SP_JSX.jsx("div", { style: { fontSize: "12px", fontWeight: "bold", color: "#64b5f6", marginBottom: "6px" }, children: candidate.source }), SP_JSX.jsx("div", { style: {
                                    fontSize: "12px",
                                    color: "rgba(255, 255, 255, 0.7)",
                                    marginBottom: "2px",
                                    wordBreak: "break-all",
                                }, children: candidate.path }), SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)" }, children: candidateDetail(candidate) }), candidate.present ? (SP_JSX.jsx("div", { style: { marginTop: "8px" }, children: SP_JSX.jsx(DFL.DialogButton, { onClick: () => onChoose(candidate.source), disabled: isLoading, children: "Use this copy" }) })) : null] }, candidate.source)))
                    : null, errorMessage ? (SP_JSX.jsx("div", { style: {
                        padding: "8px 10px",
                        background: "rgba(244, 67, 54, 0.15)",
                        borderRadius: "4px",
                        border: "1px solid rgba(244, 67, 54, 0.3)",
                        marginBottom: "12px",
                        fontSize: "12px",
                        color: "#ef9a9a",
                        lineHeight: "1.4",
                    }, children: errorMessage })) : null, SP_JSX.jsxs("div", { style: { display: "flex", justifyContent: "flex-end", gap: "8px" }, children: [chosen !== null && rebootable && (SP_JSX.jsx(DFL.DialogButton, { onClick: confirmRestartDevice, disabled: gameRunning, children: "Restart device now" })), SP_JSX.jsx(DFL.DialogButton, { onClick: onClose, disabled: isLoading, style: { opacity: 0.7 }, children: chosen === null ? "Cancel" : "Later" })] })] }) }));
};
const DataLocationModalHost = ({ closeModal }) => {
    const [candidates, setCandidates] = SP_REACT.useState(null);
    const [chosen, setChosen] = SP_REACT.useState(null);
    const [isLoading, setIsLoading] = SP_REACT.useState(false);
    const [errorMessage, setErrorMessage] = SP_REACT.useState(null);
    SP_REACT.useEffect(() => {
        let live = true;
        getDataLocationCandidates()
            .then((result) => {
            if (!live)
                return;
            setCandidates(result.candidates);
        })
            .catch((e) => {
            if (!live)
                return;
            const msg = e instanceof Error ? e.message : String(e);
            logError(`getDataLocationCandidates threw: ${msg}`);
            setErrorMessage("Could not read the older data folders.");
            setCandidates([]);
        });
        return () => {
            live = false;
        };
    }, []);
    const handleChoose = (source) => {
        setIsLoading(true);
        setErrorMessage(null);
        chooseDataLocation(source)
            .then((result) => {
            if (!result.success) {
                logError(`chooseDataLocation(${source}) failed (${result.reason}): ${result.message}`);
                setErrorMessage(result.message);
                setIsLoading(false);
                return;
            }
            setChosen(source);
            setIsLoading(false);
        })
            .catch((e) => {
            const msg = e instanceof Error ? e.message : String(e);
            logError(`chooseDataLocation(${source}) threw: ${msg}`);
            setErrorMessage(msg || "Could not record your choice.");
            setIsLoading(false);
        });
    };
    return (SP_JSX.jsx(DataLocationModal, { candidates: candidates, chosen: chosen, onChoose: handleChoose, onClose: () => closeModal?.(), isLoading: isLoading, errorMessage: errorMessage }));
};
function showDataLocationModal() {
    DFL.showModal(SP_JSX.jsx(DataLocationModalHost, {}));
}

const DATA_LOCATION_CHOICE_TITLE = "Arcoon Deck found two copies of your library";
const DATA_LOCATION_FAILED_TITLE = "Arcoon Deck could not move your data";
const CHOICE_BODY = "Two older installs of this plugin both hold a library, so Arcoon Deck has not moved anything and is still using the " +
    "copy it was given. Pick the one to keep — nothing is deleted either way.";
function dataLocationFailedMessage(reason) {
    const tail = "Nothing was lost — Arcoon Deck is still reading and writing the folders it could not move, and will try again the " +
        "next time it starts.";
    return reason ? `${reason}. ${tail}` : tail;
}
const REACHABLE_ONLY = () => { };
const DataLocationCard = ({ title, body, onActivate }) => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Focusable, { onActivate: onActivate, children: SP_JSX.jsxs("div", { "data-testid": "data-location-notice", style: {
                padding: "8px 12px",
                backgroundColor: "rgba(212, 167, 44, 0.15)",
                borderLeft: "3px solid #d4a72c",
                borderRadius: "4px",
                fontSize: "12px",
            }, children: [SP_JSX.jsxs("div", { style: { fontWeight: "bold", color: "#d4a72c", marginBottom: "4px" }, children: ["⚠️", " ", title] }), SP_JSX.jsx("div", { style: { color: "rgba(255, 255, 255, 0.7)" }, children: body })] }) }) }));
const DataLocationNotice = () => {
    const state = useDataLocationState();
    if (!state.pending)
        return null;
    if (state.kind === "failed") {
        return (SP_JSX.jsx(DataLocationCard, { title: DATA_LOCATION_FAILED_TITLE, body: dataLocationFailedMessage(state.message), onActivate: REACHABLE_ONLY }));
    }
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DataLocationCard, { title: DATA_LOCATION_CHOICE_TITLE, body: CHOICE_BODY, onActivate: showDataLocationModal }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", onClick: showDataLocationModal, children: "Choose a copy" }) })] }));
};
const DataLocationNoticeSection = () => {
    const state = useDataLocationState();
    if (!state.pending)
        return null;
    return (SP_JSX.jsx(DFL.PanelSection, { children: SP_JSX.jsx(DataLocationNotice, {}) }));
};

const MigrationConflictModal = ({ conflictCount, closeModal, onChoice }) => (SP_JSX.jsx(DFL.ModalRoot, { closeModal: closeModal, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "320px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "16px", fontWeight: "bold", color: "#fff", marginBottom: "8px" }, children: "Files Already Exist" }), SP_JSX.jsxs("div", { style: { fontSize: "13px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "16px" }, children: [conflictCount, " file(s) already exist at the destination."] }), SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: [SP_JSX.jsx(DFL.DialogButton, { onClick: () => {
                            closeModal?.();
                            onChoice("overwrite");
                        }, children: "Overwrite" }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => {
                            closeModal?.();
                            onChoice("skip");
                        }, children: "Skip" }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => closeModal?.(), style: { opacity: 0.5 }, children: "Cancel" })] })] }) }));

const MigrationBlockedPage = ({ migration }) => {
    const [migrating, setMigrating] = SP_REACT.useState(false);
    const [migrateResult, setMigrateResult] = SP_REACT.useState("");
    const runMigration = async (strategy) => {
        setMigrating(true);
        setMigrateResult("");
        try {
            const result = await migrateRetroDeckFiles(strategy);
            if (result.needs_confirmation) {
                setMigrating(false);
                DFL.showModal(SP_JSX.jsx(MigrationConflictModal, { conflictCount: result.conflict_count ?? 0, onChoice: (s) => {
                        detach(runMigration(s));
                    } }));
                return;
            }
            setMigrateResult(result.message);
            if (result.success) {
                clearMigration();
                showToast(result.message || "Migration complete.");
            }
        }
        catch {
            setMigrateResult("Migration failed");
        }
        setMigrating(false);
    };
    const handleMigrate = () => {
        detach(runMigration(null));
    };
    const handleDismiss = () => {
        DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Dismiss Migration?", strDescription: "This will accept that some ROMs and saves remain at the old location. " +
                "The plugin will continue with the new path. Save data may be inconsistent " +
                "across sessions. Are you sure?", strOKButtonText: "Dismiss", strCancelButtonText: "Cancel", onOK: () => {
                detach((async () => {
                    try {
                        const result = await dismissRetrodeckMigration();
                        if (result.success) {
                            clearMigration();
                            showToast("Migration dismissed.");
                        }
                    }
                    catch {
                        setMigrateResult("Dismiss failed");
                    }
                })());
            } }));
    };
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs(DFL.PanelSection, { title: "RetroDECK Migration Required", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs("div", { style: {
                                padding: "8px 12px",
                                backgroundColor: "rgba(212, 167, 44, 0.15)",
                                borderLeft: "3px solid #d4a72c",
                                borderRadius: "4px",
                            }, children: [SP_JSX.jsxs("div", { style: {
                                        fontSize: "13px",
                                        fontWeight: "bold",
                                        color: "#d4a72c",
                                        marginBottom: "6px",
                                    }, children: ["⚠️", " RetroDECK location changed"] }), SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "4px" }, children: ["From: ", migration.old_path ?? "unknown"] }), SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "4px" }, children: ["To: ", migration.new_path ?? "unknown"] }), SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.9)" }, children: [migration.roms_count ?? 0, " ROM(s), ", migration.bios_count ?? 0, " BIOS, ", migration.saves_count ?? 0, " save(s) to migrate"] })] }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", disabled: migrating, onClick: handleMigrate, onFocus: scrollToTop, children: migrating ? "Migrating..." : "Migrate Files" }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", disabled: migrating, onClick: handleDismiss, children: "Dismiss" }) }), migrateResult && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: migrateResult }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { style: { fontSize: "11px", color: "rgba(255, 255, 255, 0.55)", padding: "4px 0" }, children: "Or revert RetroDECK to its previous location \u2014 the plugin will detect it automatically." }) })] }), SP_JSX.jsx(LegacyInstallNotice, {}), SP_JSX.jsx(DataLocationNoticeSection, {})] }));
};

const PLAYTIME_SCOPE_TITLE = "Cross-device playtime";
const PLAYTIME_SCOPE_MESSAGE = "Sign in again to enable cross-device playtime sync.";
const PlaytimeScopeBanner = ({ onOpenConnections }) => {
    const handleDismiss = () => {
        setPlaytimeScopeState({ pending: false });
    };
    return (SP_JSX.jsxs(DFL.PanelSection, { title: PLAYTIME_SCOPE_TITLE, children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs("div", { style: {
                        padding: "8px 12px",
                        backgroundColor: "rgba(212, 167, 44, 0.15)",
                        borderLeft: "3px solid #d4a72c",
                        borderRadius: "4px",
                    }, children: [SP_JSX.jsxs("div", { style: {
                                fontSize: "13px",
                                fontWeight: "bold",
                                color: "#d4a72c",
                                marginBottom: "6px",
                            }, children: ["⚠️", " ", PLAYTIME_SCOPE_TITLE] }), SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.85)", lineHeight: 1.5 }, children: PLAYTIME_SCOPE_MESSAGE })] }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs(DFL.Focusable, { "flow-children": "horizontal", style: { display: "flex", gap: "8px" }, children: [SP_JSX.jsx(DFL.DialogButton, { style: { flex: "1 1 auto", minWidth: 0 }, onClick: onOpenConnections, children: "Open Connections" }), SP_JSX.jsx(DFL.DialogButton, { style: { flex: "1 1 auto", minWidth: 0 }, onClick: handleDismiss, children: "Dismiss" })] }) })] }));
};

function connectionFailureLabel(failure) {
    const reason = failure?.reason;
    const message = failure?.message ?? "";
    switch (reason) {
        case "auth_failed":
            return "Sign-in rejected";
        case "server_unreachable":
            return "Server unreachable";
        case "version_error":
            return "Unsupported RomM version";
        case "config_error":
            if (/server url/i.test(message))
                return "No server URL";
            if (/not signed in/i.test(message))
                return "Not signed in";
            return "Not connected";
        default:
            return "Not connected";
    }
}
const ConnectionIndicator = ({ connected, failure }) => {
    if (connected === "backend_failed") {
        return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(FaExclamationTriangle, { style: { color: "#d4a72c", fontSize: "14px" } }), SP_JSX.jsx("span", { style: { fontSize: "12px" }, children: "Backend error" })] }));
    }
    if (connected === null) {
        return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.Spinner, { width: 14, height: 14 }), SP_JSX.jsx("span", { style: { fontSize: "12px", opacity: 0.7 }, children: "Checking..." })] }));
    }
    if (connected) {
        return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(FaCheckCircle, { style: { color: "#59bf40", fontSize: "14px" } }), SP_JSX.jsx("span", { style: { fontSize: "12px" }, children: "Connected" })] }));
    }
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(FaTimesCircle, { style: { color: "#d4343c", fontSize: "14px" } }), SP_JSX.jsx("span", { style: { fontSize: "12px" }, children: connectionFailureLabel(failure) })] }));
};
function lastAttemptLine(attempt) {
    return `${attempt.status} ${formatTimeAgo(attempt.finished_at) ?? attempt.finished_at}`;
}
function lastSyncValue(stats) {
    if (stats.last_sync) {
        return (SP_JSX.jsxs("span", { style: { fontSize: "12px", display: "flex", flexDirection: "column", alignItems: "flex-end" }, children: [SP_JSX.jsx("span", { children: formatTimeAgo(stats.last_sync) ?? stats.last_sync }), stats.last_attempt && SP_JSX.jsx("span", { style: { opacity: 0.6 }, children: lastAttemptLine(stats.last_attempt) })] }));
    }
    if (stats.last_attempt) {
        return SP_JSX.jsx("span", { style: { fontSize: "12px" }, children: lastAttemptLine(stats.last_attempt) });
    }
    return SP_JSX.jsx("span", { style: { fontSize: "12px" }, children: "Never" });
}
function formatLibraryLine(stats) {
    const parts = [pluralize(stats.roms, "game")];
    if (stats.platforms > 0)
        parts.push(pluralize(stats.platforms, "platform"));
    const collections = stats.collections ?? 0;
    if (collections > 0)
        parts.push(pluralize(collections, "collection"));
    return parts.join(" · ");
}
function previewMovesACollection(summary) {
    return (!!(summary.collection_diff?.added.length || summary.collection_diff?.removed.length) ||
        !!summary.platform_collection_diff?.has_changes);
}
function previewCountsLine(preview) {
    const s = preview.summary;
    const parts = [];
    if (s.new_count > 0)
        parts.push(`${s.new_count} new`);
    if (s.changed_count > 0)
        parts.push(`${s.changed_count} updated`);
    if (s.remove_count > 0)
        parts.push(`${s.remove_count} removed`);
    if (parts.length > 0)
        return parts.join(" · ");
    if (previewMovesACollection(s))
        return "collection changes";
    return (s.cover_refresh_count ?? 0) > 0 ? "cover work only" : "ready to review";
}
const BlockSeparator = () => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { "data-testid": "block-separator", style: { height: "1px", backgroundColor: "rgba(255, 255, 255, 0.12)" } }) }));
const STATUS_SUCCESS_COLOR = "#59bf40";
const STATUS_CLEAR_MS = 15000;
const PAUSED_STATS_POLL_MS = 10000;
function terminalStatusTone(stage) {
    return stage === "done" ? "success" : "neutral";
}
const RUN_KIND_LABEL = {
    preview: "Checking for changes",
    apply: "Syncing",
};
const RUN_KIND_UNKNOWN_LABEL = "Sync in progress";
function snapshotHasAuthority(backendProgress, inFlight, stored, storeAtIssue) {
    if (!backendProgress.running && stored !== storeAtIssue)
        return false;
    const backendRunIdle = inFlight === false;
    const namesStoredRun = !!stored.runId && stored.runId === backendProgress.runId;
    const backendKnowsStoredRun = backendRunIdle && !!stored.runId;
    if (!backendProgress.running && stored.running && !namesStoredRun && !backendKnowsStoredRun)
        return false;
    return true;
}
function seededFrame(backendProgress, stored) {
    const sameRun = backendProgress.runId && stored.runId ? backendProgress.runId === stored.runId : true;
    const isSameLiveRun = backendProgress.running && stored.running && sameRun;
    const backendStage = stored.stage === "applying" ? undefined : backendProgress.stage;
    return isSameLiveRun
        ? {
            ...stored,
            running: backendProgress.running,
            ...(backendStage !== undefined ? { stage: backendStage } : {}),
            ...(backendProgress.runId !== undefined ? { runId: backendProgress.runId } : {}),
            ...(backendProgress.runKind !== undefined ? { runKind: backendProgress.runKind } : {}),
        }
        : backendProgress;
}
const MainPage = ({ onNavigate }) => {
    const stats = useSyncStats();
    const { connected, failure: connectionFailure } = useConnectionProbe();
    const versionError = useVersionError();
    const [cancelling, setCancelling] = SP_REACT.useState(false);
    const [status, setStatus] = SP_REACT.useState(null);
    const preview = usePendingPreview();
    const [previewNowMs, setPreviewNowMs] = SP_REACT.useState(null);
    const [retroarchWarning, setRetroarchWarning] = SP_REACT.useState(null);
    const [retrodeckBanner, setRetrodeckBanner] = SP_REACT.useState(null);
    const migration = useMigrationStatus();
    const settingsReset = useSettingsResetState();
    const playtimeScope = usePlaytimeScopeState();
    const saveSortMigration = useSaveSortMigrationState();
    const downloads = useDownloads();
    const statusTimeoutRef = SP_REACT.useRef(null);
    const showTransientStatus = (text, tone = "neutral") => {
        if (statusTimeoutRef.current)
            clearTimeout(statusTimeoutRef.current);
        setStatus({ text, tone });
        statusTimeoutRef.current = setTimeout(() => setStatus(null), STATUS_CLEAR_MS);
    };
    const run = useSyncRunView({
        onRunEnd: (progress) => {
            setCancelling(false);
            showTransientStatus(progress.message || "Sync finished", terminalStatusTone(progress.stage));
            setPreviewNowMs(Date.now());
            if (getPendingPreviewSnapshot() === null)
                detach(refreshPendingPreview());
            detach(refreshSyncStatsAfterChange());
        },
        onTerminalWording: (message, stage) => showTransientStatus(message, terminalStatusTone(stage)),
    });
    const syncing = run.running;
    SP_REACT.useEffect(() => {
        refreshMigrationState()
            .then(({ retrodeck, save_sort }) => {
            setMigrationStatus(retrodeck);
            setSaveSortMigrationStatus(save_sort);
        })
            .catch((e) => logError(`Failed to refresh migration state: ${e}`));
        detach(refreshSyncStats());
        getSettings()
            .then((s) => {
            if (s.retroarch_input_check) {
                setRetroarchWarning(s.retroarch_input_check);
            }
        })
            .catch((e) => logError(`Failed to load settings: ${e}`));
        getRetroDeckStatus()
            .then((s) => setRetrodeckBanner(retroDeckBanner(s.status, s)))
            .catch((e) => logError(`Failed to query RetroDECK status: ${e}`));
        detach(refreshPendingPreview().then(() => setPreviewNowMs(Date.now())));
        fetchPlaytimeScopeState().catch((e) => logError(`Failed to check playtime scope notice: ${e}`));
        const storeAtIssue = getSyncProgress();
        getSyncStatus()
            .then(({ inFlight, ...backendProgress }) => {
            const stored = getSyncProgress();
            if (!snapshotHasAuthority(backendProgress, inFlight, stored, storeAtIssue))
                return;
            setSyncProgress(seededFrame(backendProgress, stored));
        })
            .catch((e) => logError(`Failed to query sync status: ${e}`));
        return () => {
            if (statusTimeoutRef.current)
                clearTimeout(statusTimeoutRef.current);
        };
    }, []);
    const pendingPreview = syncing ? null : preview;
    const previewExpired = pendingPreview !== null && previewNowMs !== null && previewSecondsLeft(pendingPreview, previewNowMs) === 0;
    const previewDeadline = pendingPreview?.expires_at;
    SP_REACT.useEffect(() => {
        if (previewDeadline === undefined)
            return;
        const untilExpiry = previewDeadline * 1000 - Date.now();
        if (untilExpiry <= 0)
            return;
        const timer = setTimeout(() => setPreviewNowMs(Date.now()), untilExpiry);
        return () => clearTimeout(timer);
    }, [previewDeadline]);
    const lastRunPaused = stats?.last_attempt?.status === "paused";
    SP_REACT.useEffect(() => {
        if (syncing || !lastRunPaused)
            return;
        const id = setInterval(() => detach(refreshSyncStats()), PAUSED_STATS_POLL_MS);
        return () => clearInterval(id);
    }, [syncing, lastRunPaused]);
    const handleCancel = async () => {
        setCancelling(true);
        requestSyncCancel();
        try {
            await cancelSync(getSyncProgress().runId ?? "");
        }
        catch {
            setCancelling(false);
            showTransientStatus("Failed to cancel sync");
        }
    };
    const activeDownloads = downloads.filter((d) => d.status === "queued" || d.status === "downloading");
    const completedDownloads = downloads.filter((d) => d.status === "completed" || d.status === "failed" || d.status === "cancelled");
    const hasDownloads = activeDownloads.length > 0 || completedDownloads.length > 0;
    let slot = null;
    if (syncing) {
        slot = {
            label: run.runKind === null ? RUN_KIND_UNKNOWN_LABEL : RUN_KIND_LABEL[run.runKind],
            value: run.totalSteps ? `${run.step} of ${run.totalSteps}` : "",
            bar: true,
        };
    }
    else if (pendingPreview && !previewExpired) {
        slot = { label: "Changes ready", value: previewCountsLine(pendingPreview), bar: false };
    }
    if (versionError) {
        return SP_JSX.jsx(VersionErrorCard, { message: versionError, compact: true });
    }
    if (migration.pending) {
        return SP_JSX.jsx(MigrationBlockedPage, { migration: migration });
    }
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(LegacyInstallNotice, {}), settingsReset.pending && SP_JSX.jsx(SettingsResetBanner, { backedUpTo: settingsReset.backedUpTo }), playtimeScope.pending && (SP_JSX.jsx(PlaytimeScopeBanner, { onOpenConnections: () => onNavigate({ page: "settings", section: "connections" }) })), SP_JSX.jsxs(DFL.PanelSection, { children: [retrodeckBanner && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Focusable, { onActivate: () => { }, children: SP_JSX.jsx(WarningCard, { title: retrodeckBanner.title, message: retrodeckBanner.message, compact: true }) }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Connection", focusable: true, bottomSeparator: "none", description: connected === "backend_failed" ? "Plugin backend failed to start — check Decky logs." : undefined, children: SP_JSX.jsx("div", { style: { display: "flex", alignItems: "center", gap: "6px" }, children: SP_JSX.jsx(ConnectionIndicator, { connected: connected, failure: connectionFailure }) }) }) }), stats && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Last sync", focusable: true, bottomSeparator: "none", childrenContainerWidth: "max", children: lastSyncValue(stats) }) }), stats.roms > 0 && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Library", description: SP_JSX.jsx("div", { style: { width: "100%", textAlign: "right", fontSize: "12px" }, children: formatLibraryLine(stats) }), focusable: true, bottomSeparator: "none" }) }))] })), slot && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: SP_JSX.jsx("span", { "data-testid": "sync-slot-label", children: slot.label }), focusable: true, onActivate: () => onNavigate("sync"), bottomSeparator: "none", ...(slot.bar
                                ? {
                                    description: (SP_JSX.jsx(DFL.ProgressBar, { indeterminate: run.coarseFraction === undefined, ...(run.coarseFraction !== undefined ? { nProgress: run.coarseFraction } : {}) })),
                                }
                                : {}), children: SP_JSX.jsx("span", { "data-testid": "sync-slot-value", style: { fontSize: "12px" }, children: slot.value }) }) })), syncing && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", disabled: cancelling, onClick: () => {
                                detach(handleCancel());
                            }, children: cancelling ? "Cancelling…" : "Cancel Sync" }) })), status?.text && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: SP_JSX.jsx("span", { "data-testid": "sync-status", style: {
                                    ...wrapText,
                                    ...(status.tone === "success" ? { color: STATUS_SUCCESS_COLOR } : {}),
                                }, children: status.text }), focusable: true, bottomSeparator: "none" }) })), retroarchWarning?.warning && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "RetroArch: input_driver issue", description: `Using "${retroarchWarning.current}" \u2014 controller navigation in RetroArch menus may not work.`, focusable: true, bottomSeparator: "none" }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", onClick: () => onNavigate({ page: "settings", section: "controller" }), children: "Open Controller" }) })] })), saveSortMigration.pending && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Focusable, { onActivate: () => { }, children: SP_JSX.jsxs("div", { style: {
                                            padding: "8px 12px",
                                            backgroundColor: "rgba(212, 167, 44, 0.15)",
                                            borderLeft: "3px solid #d4a72c",
                                            borderRadius: "4px",
                                            fontSize: "12px",
                                        }, children: [SP_JSX.jsxs("div", { style: { fontWeight: "bold", color: "#d4a72c", marginBottom: "4px" }, children: ["\u26A0\uFE0F", " RetroArch save sorting changed"] }), SP_JSX.jsxs("div", { style: { color: "rgba(255, 255, 255, 0.7)" }, children: [saveSortMigration.saves_count ?? 0, " save file(s) to migrate"] })] }) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", onClick: () => onNavigate({ page: "settings", section: "save-sync" }), children: "Open Save Sync" }) })] })), lastRunPaused && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Focusable, { onActivate: () => { }, children: SP_JSX.jsxs("div", { "data-testid": "sync-paused-notice", style: {
                                            padding: "8px 12px",
                                            backgroundColor: "rgba(61, 157, 246, 0.15)",
                                            borderLeft: "3px solid #3d9df6",
                                            borderRadius: "4px",
                                            fontSize: "12px",
                                        }, children: [SP_JSX.jsx("div", { style: { fontWeight: "bold", color: "#3d9df6", marginBottom: "4px" }, children: "Sync paused" }), SP_JSX.jsx("div", { style: { color: "rgba(255, 255, 255, 0.7)" }, children: "The last run stopped at a safe point to protect Steam's memory. Restarting Steam and resuming it are on the Sync page." })] }) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", onClick: () => onNavigate("sync"), children: "Open Sync" }) })] })), SP_JSX.jsx(DataLocationNotice, {}), SP_JSX.jsx(BlockSeparator, {})] }), hasDownloads && (SP_JSX.jsxs(DFL.PanelSection, { children: [activeDownloads.slice(0, 2).map((item) => (SP_JSX.jsx(DownloadProgressRow, { caption: item.rom_name, bytesDownloaded: item.bytes_downloaded, totalBytes: item.total_bytes }, item.rom_id))), activeDownloads.length > 2 && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: `+${activeDownloads.length - 2} more downloading`, focusable: true, bottomSeparator: "none" }) })), completedDownloads.length > 0 && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: `${pluralize(completedDownloads.length, "download")} completed`, focusable: true, bottomSeparator: "none" }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", onClick: () => onNavigate("downloads"), children: "View All" }) }), SP_JSX.jsx(BlockSeparator, {})] })), SP_JSX.jsxs(DFL.PanelSection, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { [ENTRY_STOP_ATTR]: "", style: { display: "contents" }, children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", onClick: () => onNavigate("sync"), children: "Sync" }) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", onClick: () => onNavigate("library"), children: "Library" }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", onClick: () => onNavigate("settings"), children: "Settings" }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", bottomSeparator: "none", onClick: () => onNavigate("data"), children: "Data Management" }) })] })] }));
};

function trimServerUrl(url) {
    return url.trim();
}
function isValidServerUrl(url) {
    const trimmed = trimServerUrl(url);
    return /^https?:\/\/.+/i.test(trimmed);
}
function isHttpsUrl(url) {
    return trimServerUrl(url).toLowerCase().startsWith("https://");
}

const WIDE_ROOT_CLASS = "romm-wide-qam-root";

const BOUNDS = { height: "100%", minHeight: 0, overscrollBehavior: "contain" };
const AFTER_STEAMS_OWN_SCROLL_MS = 50;
function revealTop(region, focused) {
    const focusedBottom = offsetWithinScroller(focused, region) + focused.getBoundingClientRect().height;
    if (focusedBottom > region.clientHeight)
        return false;
    setTimeout(() => region.scrollTo({ top: 0, behavior: "smooth" }), AFTER_STEAMS_OWN_SCROLL_MS);
    return true;
}
function revealBottom(region, focused) {
    if (region.scrollHeight - offsetWithinScroller(focused, region) > region.clientHeight)
        return false;
    setTimeout(() => region.scrollTo({ top: region.scrollHeight, behavior: "smooth" }), AFTER_STEAMS_OWN_SCROLL_MS);
    return true;
}
function revealEdge(event) {
    const region = event.currentTarget;
    const focused = event.target;
    const view = region.ownerDocument.defaultView;
    if (!view || !(focused instanceof view.HTMLElement) || region.scrollHeight <= region.clientHeight)
        return;
    const stops = [...region.querySelectorAll(FOCUS_STOPS)];
    const reached = stops.indexOf(focused);
    if (reached < 0)
        return;
    const isFirst = !stops.slice(0, reached).some((stop) => !stop.contains(focused));
    const isLast = !stops.slice(reached + 1).some((stop) => !focused.contains(stop));
    if (isFirst && revealTop(region, focused))
        return;
    if (isLast)
        revealBottom(region, focused);
}
const ScrollRegion = ({ style, testId, children }) => {
    const marker = testId === undefined ? {} : { "data-testid": testId };
    return (ScrollPanel ? (SP_JSX.jsx(ScrollPanel, { style: { ...BOUNDS, ...style }, onFocus: revealEdge, ...marker, children: children })) : (SP_JSX.jsx(DFL.Focusable, { style: { ...BOUNDS, overflow: "auto", ...style }, onFocus: revealEdge, ...marker, children: children })));
};

const OWNS_ENTRY_FOCUS_ATTR = "data-romm-owns-entry-focus";
const MIN_BODY_HEIGHT = 240;
const BackChipLabel = () => ControllerGlyph ? (SP_JSX.jsxs("span", { style: { display: "inline-flex", alignItems: "center", gap: "5px" }, children: [SP_JSX.jsx(ControllerGlyph, { button: GLYPH_BUTTON_B, bKnockout: true, style: { width: "13px", height: "13px" } }), "Back"] })) : (SP_JSX.jsx(SP_JSX.Fragment, { children: "\u2039 Back" }));
function scrollingAncestor(body, view) {
    for (let el = body.parentElement; el; el = el.parentElement) {
        const overflowY = view.getComputedStyle(el).overflowY;
        if (overflowY === "auto" || overflowY === "scroll")
            return el;
    }
    return null;
}
function ancestorOverhang(body, scroller) {
    let total = 0;
    for (let el = body; el && el !== scroller; el = el.parentElement) {
        const parent = el.parentElement;
        if (!parent || parent === scroller)
            break;
        total += Math.max(0, el.getBoundingClientRect().bottom - parent.getBoundingClientRect().bottom);
    }
    return total;
}
function measureBodyFit(body, view) {
    const scroller = scrollingAncestor(body, view);
    const remaining = scroller
        ? scroller.clientHeight - offsetWithinScroller(body, scroller)
        : view.innerHeight - body.getBoundingClientRect().top;
    return {
        height: Math.max(MIN_BODY_HEIGHT, remaining),
        overhang: scroller ? ancestorOverhang(body, scroller) : 0,
    };
}
const WidePage = ({ title, onBack, tabs, activeTab, onShowTab, children, ownRegions }) => {
    const rootRef = SP_REACT.useRef(null);
    const bodyRef = SP_REACT.useRef(null);
    const [fit, setFit] = SP_REACT.useState(null);
    SP_REACT.useLayoutEffect(() => {
        const body = bodyRef.current;
        const view = body?.ownerDocument.defaultView;
        if (!body || !view)
            return;
        const measure = () => {
            const next = measureBodyFit(body, view);
            setFit((previous) => (previous?.height === next.height && previous.overhang === next.overhang ? previous : next));
        };
        measure();
        const observer = new view.ResizeObserver(measure);
        observer.observe(body.ownerDocument.documentElement);
        const scroller = scrollingAncestor(body, view);
        if (scroller)
            observer.observe(scroller);
        return () => observer.disconnect();
    }, []);
    const steamPlacesFocus = Boolean(tabs && Tabs);
    SP_REACT.useEffect(() => {
        const body = bodyRef.current;
        if (steamPlacesFocus || !body)
            return;
        const timer = setTimeout(() => placeEntryFocus(body, pageEntryStop), ENTRY_FOCUS_DELAY_MS);
        return () => clearTimeout(timer);
    }, [steamPlacesFocus]);
    const bodyStyle = { height: fit === null ? undefined : `${fit.height}px`, overflow: "hidden" };
    const rootStyle = fit === null ? undefined : { marginBottom: `${-fit.overhang}px` };
    let body = ownRegions ? children : SP_JSX.jsx(ScrollRegion, { children: children });
    if (tabs) {
        body = Tabs ? (SP_JSX.jsx(Tabs, { tabs: tabs, activeTab: activeTab, onShowTab: onShowTab, autoFocusContents: true, cancelSkipTabHeader: true })) : (tabs.find((tab) => tab.id === activeTab)?.content);
    }
    return (SP_JSX.jsxs("div", { className: WIDE_ROOT_CLASS, ref: rootRef, style: rootStyle, [OWNS_ENTRY_FOCUS_ATTR]: "", children: [SP_JSX.jsxs(DFL.Focusable, { style: { display: "flex", alignItems: "center", gap: "10px", padding: "4px 16px 6px" }, children: [SP_JSX.jsx(DFL.DialogButton, { style: { flex: "0 0 auto", minWidth: 0, width: "auto", padding: "4px 10px", fontSize: "13px" }, onClick: onBack, children: SP_JSX.jsx(BackChipLabel, {}) }), SP_JSX.jsx("span", { style: { fontSize: "16px", fontWeight: 600, color: "#dcdedf" }, children: title })] }), SP_JSX.jsx("div", { ref: bodyRef, style: bodyStyle, "data-testid": "wide-page-body", children: body })] }));
};

const ListDetail = ({ items, selectedId, onSelect, renderDetail, listHeader, selectOnActivate, }) => (SP_JSX.jsxs("div", { style: { height: "100%", minHeight: 0, overflowY: "auto" }, children: [SP_JSX.jsxs(DFL.Focusable, { "flow-children": "vertical", children: [listHeader, items.map((item) => (SP_JSX.jsx("div", { style: { display: "contents" }, ...(item.id === selectedId ? { [ENTRY_STOP_ATTR]: "" } : {}), children: SP_JSX.jsx(DFL.Focusable, { onFocus: () => {
                            if (item.id !== selectedId)
                                onSelect(item.id);
                        }, ...(selectOnActivate ? { onActivate: () => onSelect(item.id) } : {}), children: item.render(item.id === selectedId) }) }, item.id)))] }), SP_JSX.jsx("div", { style: { borderTop: "1px solid rgba(255, 255, 255, 0.12)", marginTop: "8px" }, children: SP_JSX.jsx(DFL.Focusable, { "flow-children": "vertical", children: renderDetail(selectedId) }) })] }));

const SECONDARY_FONT = "11px";
const MUTED = "#8f98a0";
const RED = "#d94126";
const GREEN = "#5ba32b";
const AMBER = "#d4a72c";
const PALE_GREEN = "#8fc46b";
const VIOLET = "#a48fd4";
const ROW_MARKER_WIDTH = 3;
const ROW_MARKER_GAP = 5;
const ROW_CONTENT_INSET = ROW_MARKER_WIDTH + ROW_MARKER_GAP;
const SELECTION_ACCENT = "#1a9fff";
const PANE_GUTTER = "16px";
const TABLE_LINE = "1px solid rgba(255, 255, 255, 0.12)";
const PANE_TABLE_REGISTER = {
    rowPadding: `4px ${PANE_GUTTER}`,
    headerPadding: `0 ${PANE_GUTTER} 4px`,
};
const CELL_CLIP = {
    minWidth: 0,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap",
};
const asCell = (cell) => (typeof cell === "string" ? { content: cell } : cell);
const cellStyle = (cell) => ({ ...(cell.clip === false ? {} : CELL_CLIP), ...cell.style });
const COLUMN_GAP = "8px";
const Cells = ({ cells }) => (SP_JSX.jsx(SP_JSX.Fragment, { children: cells.map((cell, index) => (SP_JSX.jsx("span", { style: cellStyle(cell), ...(cell.title === undefined ? {} : { title: cell.title }), children: cell.content }, index))) }));
const PaneTableHeader = ({ columns, cells, register = PANE_TABLE_REGISTER, testId }) => (SP_JSX.jsx("div", { ...(testId === undefined ? {} : { "data-testid": testId }), style: {
        display: "grid",
        gridTemplateColumns: columns,
        gap: COLUMN_GAP,
        padding: register.headerPadding,
        ...(register.rule ? { borderBottom: TABLE_LINE } : {}),
        fontSize: SECONDARY_FONT,
        color: MUTED,
    }, children: SP_JSX.jsx(Cells, { cells: cells.map(asCell) }) }));
const PaneTableRow = ({ columns, cells, register = PANE_TABLE_REGISTER, style, testId, focusStop = true, children }) => {
    const body = (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("div", { style: { display: "grid", gridTemplateColumns: columns, gap: COLUMN_GAP, alignItems: "center" }, children: SP_JSX.jsx(Cells, { cells: cells }) }), children] }));
    const wrapperStyle = {
        padding: register.rowPadding,
        ...(register.rowFont === undefined ? {} : { fontSize: register.rowFont }),
        ...(register.rowLineHeight === undefined ? {} : { lineHeight: register.rowLineHeight }),
        ...style,
    };
    const marker = testId === undefined ? {} : { "data-testid": testId };
    return focusStop ? (SP_JSX.jsx(DFL.Focusable, { onActivate: () => { }, style: wrapperStyle, ...marker, children: body })) : (SP_JSX.jsx("div", { style: wrapperStyle, ...marker, children: body }));
};
const FLAT_BUTTON = { flex: "1 1 auto", minWidth: 0, padding: "6px 10px", fontSize: "13px" };
const ROW_BUTTON = { width: "100%", minWidth: 0, padding: "4px", fontSize: "11px" };
const SectionTitle = ({ title, note, noteColor }) => (SP_JSX.jsxs("div", { style: { display: "flex", alignItems: "baseline", gap: "8px", padding: "12px 16px 4px" }, children: [SP_JSX.jsx("span", { style: { fontSize: "12px", fontWeight: 600, letterSpacing: "0.5px", color: "#dcdedf" }, children: title.toUpperCase() }), note && SP_JSX.jsx("span", { style: { fontSize: SECONDARY_FONT, color: noteColor ?? MUTED }, children: note })] }));
const Muted = ({ children }) => (SP_JSX.jsx("div", { style: { fontSize: SECONDARY_FONT, color: MUTED, padding: "0 16px 6px" }, children: children }));
const ButtonRow = ({ padding, children }) => (SP_JSX.jsx(DFL.Focusable, { "flow-children": "horizontal", style: { display: "flex", gap: "8px", padding }, children: children }));
function GroupStatus({ status, forKey, scope, }) {
    return status?.key === forKey && status.scope === scope ? (SP_JSX.jsx("div", { "data-testid": `status-${scope}`, style: { fontSize: "12px", color: "#dcdedf", padding: "0 16px 8px" }, children: status.text })) : null;
}
const BusyElsewhere = ({ busyKey, ownKey, busyName, }) => {
    if (busyKey === null || busyKey === ownKey)
        return null;
    return SP_JSX.jsx(Muted, { children: `Working on ${busyName} — actions here are paused until it finishes.` });
};

const pendingEdits = {};
const TextInputModal = ({ label, value: initial, field, bIsPassword, closeModal, onSubmit, }) => {
    const [value, setValue] = SP_REACT.useState(initial);
    const canSubmit = value.trim() !== "";
    const handleOK = () => {
        if (field) {
            pendingEdits[field] = value;
        }
        onSubmit(value);
    };
    return (SP_JSX.jsx(DFL.ConfirmModal, { ...(closeModal !== undefined ? { closeModal } : {}), onOK: handleOK, bOKDisabled: !canSubmit, strTitle: label, bDisableBackgroundDismiss: true, children: SP_JSX.jsx(DFL.TextField, { focusOnMount: true, label: label, value: value, ...(bIsPassword !== undefined ? { bIsPassword } : {}), onChange: (e) => setValue(e.target.value), onKeyDown: (e) => {
                if (e.key === "Enter" && canSubmit) {
                    handleOK();
                    closeModal?.();
                }
            } }) }));
};

function formatRelativeTime(isoStr) {
    if (!isoStr)
        return "never";
    const date = new Date(isoStr);
    if (Number.isNaN(date.getTime()))
        return "unknown";
    const diffMs = Date.now() - date.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1)
        return "just now";
    if (diffMin < 60)
        return `${diffMin}m ago`;
    if (diffMin < 1440)
        return `${Math.floor(diffMin / 60)}h ago`;
    const d = date.getDate();
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    return `${d} ${months[date.getMonth()]}`;
}
function sortLabel(settings) {
    return `Sort by content: ${settings.sort_by_content ? "ON" : "OFF"}, Sort by core: ${settings.sort_by_core ? "ON" : "OFF"}`;
}

const SaveSortMigrationSection = ({ migration, migrating, result, onMigrate, onDismiss, }) => {
    return (SP_JSX.jsxs(DFL.PanelSection, { title: "Save Sort Migration", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs("div", { style: {
                        padding: "8px 12px",
                        backgroundColor: "rgba(212, 167, 44, 0.15)",
                        borderLeft: "3px solid #d4a72c",
                        borderRadius: "4px",
                    }, children: [SP_JSX.jsxs("div", { style: { fontSize: "13px", fontWeight: "bold", color: "#d4a72c", marginBottom: "6px" }, children: ["⚠️", " RetroArch save sorting changed"] }), migration.old_settings && (SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "4px" }, children: ["From: ", sortLabel(migration.old_settings)] })), migration.new_settings && (SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.7)", marginBottom: "4px" }, children: ["To: ", sortLabel(migration.new_settings)] })), SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.9)" }, children: [migration.saves_count ?? 0, " save file(s) to migrate"] })] }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", disabled: migrating, onClick: onMigrate, children: migrating ? "Migrating..." : "Migrate Save Files" }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", disabled: migrating, onClick: onDismiss, children: "Dismiss (I migrated manually)" }) }), result && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: result, focusable: true }) }))] }));
};

const modalBodyStyle = { padding: "16px", minWidth: "360px" };
const titleStyle = { fontSize: "16px", fontWeight: "bold", marginBottom: "12px", color: "#fff" };
const errorStyle = { color: "#d94126", fontSize: "13px", marginTop: "12px", marginBottom: "4px" };
const footerStyle = { display: "flex", gap: "8px", marginTop: "16px" };
const footerButtonStyle = { flex: "1 1 0px", minWidth: 0 };
const ValidatingModalShell = ({ closeModal, title, error, errorTestId, submitLabel, submitDisabled, onSubmit, children, }) => (SP_JSX.jsx(DFL.ModalRoot, { ...(closeModal === undefined ? {} : { closeModal }), children: SP_JSX.jsxs("div", { style: modalBodyStyle, children: [SP_JSX.jsx("div", { style: titleStyle, children: title }), children, error !== null && (SP_JSX.jsx("div", { style: errorStyle, "data-testid": errorTestId, children: error })), SP_JSX.jsxs(DFL.Focusable, { "flow-children": "horizontal", style: footerStyle, children: [SP_JSX.jsx(DFL.DialogButton, { style: footerButtonStyle, disabled: submitDisabled, onClick: onSubmit, children: submitLabel }), SP_JSX.jsx(DFL.DialogButton, { style: footerButtonStyle, onClick: () => {
                            closeModal?.();
                        }, children: "Cancel" })] })] }) }));

const CODE_LENGTH = 8;
const CODE_GROUP = 4;
const CODE_INDICES = Array.from({ length: CODE_LENGTH }, (_unused, i) => i);
const GENERIC_SIGN_IN_ERROR$1 = "Sign-in failed. Check your connection and try again.";
const SIGN_IN_TIMEOUT_MS = 60000;
const SIGN_IN_TIMEOUT_ERROR = "The plugin backend never answered. Reload Decky or restart Steam, then try again.";
const helperTextStyle$2 = { fontSize: "12px", marginBottom: "12px", color: "rgba(255,255,255,0.6)" };
const codeLabelStyle = {
    fontSize: "12px",
    fontWeight: 600,
    marginBottom: "8px",
    color: "rgba(255,255,255,0.6)",
};
const codeRowStyle = {
    display: "flex",
    flexWrap: "nowrap",
    justifyContent: "center",
    alignItems: "center",
    gap: "6px",
    width: "100%",
};
const codeBoxWrapperStyle = { flexShrink: 0, width: "36px", height: "48px", display: "flex" };
const codeBoxFieldStyle = {
    minWidth: 0,
    width: "100%",
    height: "100%",
    boxSizing: "border-box",
    padding: "0",
    textAlign: "center",
    fontSize: "20px",
    lineHeight: "1.2",
};
const codeSeparatorStyle = {
    flexShrink: 0,
    height: "48px",
    display: "flex",
    alignItems: "center",
    fontSize: "18px",
    lineHeight: 1,
    color: "rgba(255,255,255,0.6)",
};
const normalizePairingCode = (value) => value.replace(/[^A-Za-z0-9]/g, "").toUpperCase();
const ConnectModal = ({ closeModal, onConnect, onConnectToken, onConnectPairing }) => {
    const [mode, setMode] = SP_REACT.useState("pairing");
    const [username, setUsername] = SP_REACT.useState("");
    const [password, setPassword] = SP_REACT.useState("");
    const [token, setToken] = SP_REACT.useState("");
    const [code, setCode] = SP_REACT.useState(() => new Array(CODE_LENGTH).fill(""));
    const [submitting, setSubmitting] = SP_REACT.useState(false);
    const [error, setError] = SP_REACT.useState(null);
    const codeRowRef = SP_REACT.useRef(null);
    const credentialsRowRef = SP_REACT.useRef(null);
    const boxInputAt = (index) => codeRowRef.current?.querySelectorAll("input")[index] ?? null;
    const focusBox = (index) => {
        boxInputAt(index)?.focus();
    };
    const focusBoxAtEnd = (index) => {
        const input = boxInputAt(index);
        if (!input)
            return;
        input.focus();
        const end = input.value.length;
        input.setSelectionRange(end, end);
    };
    const setBoxChar = (index, char) => {
        setCode((prev) => prev.map((current, idx) => (idx === index ? char : current)));
    };
    const distributeChars = (start, chars) => {
        setCode((prev) => {
            const next = [...prev];
            for (let offset = 0; offset < chars.length && start + offset < CODE_LENGTH; offset += 1) {
                next[start + offset] = chars.charAt(offset);
            }
            return next;
        });
        const filledThrough = start + chars.length;
        if (filledThrough >= CODE_LENGTH) {
            document.activeElement?.blur();
        }
        else {
            focusBox(filledThrough);
        }
    };
    const computeCanSubmit = () => {
        if (mode === "credentials")
            return username.trim() !== "" && password !== "";
        if (mode === "token")
            return token.trim() !== "";
        return code.every((c) => c !== "");
    };
    const canSubmit = computeCanSubmit();
    const attemptSignIn = () => {
        if (mode === "token")
            return onConnectToken(token);
        if (mode === "pairing")
            return onConnectPairing(code.join(""));
        return onConnect(username, password);
    };
    const submit = async () => {
        if (!canSubmit || submitting)
            return;
        setSubmitting(true);
        setError(null);
        try {
            const result = await withTimeout(attemptSignIn(), SIGN_IN_TIMEOUT_MS);
            if (result.success) {
                closeModal?.();
            }
            else {
                setError(result.message);
            }
        }
        catch (e) {
            setError(e instanceof TimeoutError ? SIGN_IN_TIMEOUT_ERROR : GENERIC_SIGN_IN_ERROR$1);
        }
        finally {
            setSubmitting(false);
        }
    };
    const handleBoxChange = (index) => (e) => {
        setError(null);
        const incoming = normalizePairingCode(e.target.value);
        if (incoming.length <= 1) {
            setBoxChar(index, incoming);
            if (incoming.length === 1)
                focusBox(index + 1);
            return;
        }
        const existing = code[index] ?? "";
        const fresh = existing.length > 0 && incoming.startsWith(existing) ? incoming.slice(existing.length) : incoming;
        distributeChars(index, fresh);
    };
    const handleBoxKeyDown = (index) => (e) => {
        if (e.key === "Backspace" && (code[index] ?? "") === "" && index > 0) {
            focusBoxAtEnd(index - 1);
            return;
        }
        if (e.key === "Enter") {
            e.preventDefault();
            e.stopPropagation();
            if (code.every((c) => c !== ""))
                void submit();
        }
    };
    const handleUsernameKeyDown = (e) => {
        if (e.key !== "Enter")
            return;
        e.preventDefault();
        e.stopPropagation();
        credentialsRowRef.current?.querySelectorAll("input")[1]?.focus();
    };
    const handleCompletingKeyDown = (e) => {
        if (e.key !== "Enter")
            return;
        e.preventDefault();
        e.stopPropagation();
        if (canSubmit)
            void submit();
    };
    const handleModeChange = (option) => {
        setMode(option.data);
        setError(null);
    };
    const handleUsernameChange = (e) => {
        setUsername(e.target.value);
        setError(null);
    };
    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
        setError(null);
    };
    const handleTokenChange = (e) => {
        setToken(e.target.value);
        setError(null);
    };
    return (SP_JSX.jsxs(ValidatingModalShell, { ...(closeModal === undefined ? {} : { closeModal }), title: "Sign in to RomM", error: error, errorTestId: "signin-error", submitLabel: submitting ? "Signing in…" : "Sign in", submitDisabled: !canSubmit || submitting, onSubmit: () => {
            void submit();
        }, children: [SP_JSX.jsx(DFL.DropdownItem, { label: "Sign-in method", rgOptions: [
                    { data: "pairing", label: "Pairing code" },
                    { data: "token", label: "API token" },
                    { data: "credentials", label: "Username & password" },
                ], selectedOption: mode, onChange: handleModeChange }), mode === "token" && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("div", { style: helperTextStyle$2, children: "Create a token in RomM's web UI (Settings \u2192 API Tokens) and paste it here. Make sure it has the scopes listed in the plugin docs so downloads, saves, and device sync work. The plugin never deletes a pasted token; you manage it in RomM." }), SP_JSX.jsx(DFL.Focusable, { children: SP_JSX.jsx(DFL.TextField, { focusOnMount: true, label: "API Token", value: token, bIsPassword: true, onChange: handleTokenChange, onKeyDown: handleCompletingKeyDown }) })] })), mode === "pairing" && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs("div", { style: helperTextStyle$2, children: ["In RomM's web UI open your API token and click ", SP_JSX.jsx("strong", { children: "Pair" }), ", then enter the 8-character code here within 60 seconds. The plugin fetches the token itself \u2014 nothing to copy or paste."] }), SP_JSX.jsx("div", { style: codeLabelStyle, children: "Pairing code" }), SP_JSX.jsx(DFL.Focusable, { "flow-children": "horizontal", ref: codeRowRef, style: codeRowStyle, "data-testid": "pairing-code-row", children: CODE_INDICES.map((i) => (SP_JSX.jsxs(SP_REACT.Fragment, { children: [i === CODE_GROUP && SP_JSX.jsx("span", { style: codeSeparatorStyle, children: "-" }), SP_JSX.jsx("div", { style: codeBoxWrapperStyle, children: SP_JSX.jsx(DFL.TextField, { focusOnMount: i === 0, style: codeBoxFieldStyle, value: code[i] ?? "", onChange: handleBoxChange(i), onKeyDown: handleBoxKeyDown(i) }) })] }, i))) })] })), mode === "credentials" && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("div", { style: helperTextStyle$2, children: "Enter your RomM username and password once. The plugin exchanges them for an API token and never stores your password." }), SP_JSX.jsxs("div", { ref: credentialsRowRef, "data-testid": "credentials-row", children: [SP_JSX.jsx(DFL.TextField, { focusOnMount: true, label: "Username", value: username, onChange: handleUsernameChange, onKeyDown: handleUsernameKeyDown }), SP_JSX.jsx(DFL.TextField, { label: "Password", value: password, bIsPassword: true, onChange: handlePasswordChange, onKeyDown: handleCompletingKeyDown })] })] }))] }));
};

const helperTextStyle$1 = { fontSize: "12px", marginBottom: "12px", color: "rgba(255,255,255,0.6)" };
const rowStyle = { marginBottom: "12px" };
const removeButtonStyle = { marginTop: "6px", minWidth: "auto", width: "auto" };
const emptyStyle = { fontSize: "12px", marginBottom: "8px", color: "rgba(255,255,255,0.6)" };
const STORED_VALUE_HINT = "stored — leave blank to keep it";
const GENERIC_SAVE_ERROR$1 = "Could not save the headers. Check your connection and try again.";
const storedValuePlaceholder = { placeholder: "••••" };
const keepsStoredValue = (row) => row.storedName !== null && row.value === "" && row.name === row.storedName;
const CustomHeadersModal = ({ closeModal, storedNames, onSave }) => {
    const nextId = SP_REACT.useRef(storedNames.length);
    const [rows, setRows] = SP_REACT.useState(() => storedNames.map((name, index) => ({ id: index, name, value: "", storedName: name })));
    const [submitting, setSubmitting] = SP_REACT.useState(false);
    const [error, setError] = SP_REACT.useState(null);
    const updateRow = (id, patch) => {
        setRows((prev) => prev.map((row) => (row.id === id ? { ...row, ...patch } : row)));
        setError(null);
    };
    const addRow = () => {
        const id = nextId.current;
        nextId.current += 1;
        setRows((prev) => [...prev, { id, name: "", value: "", storedName: null }]);
        setError(null);
    };
    const removeRow = (id) => {
        setRows((prev) => prev.filter((row) => row.id !== id));
        setError(null);
    };
    const toEntries = () => rows.map((row) => keepsStoredValue(row)
        ? { name: row.name, value_action: "keep" }
        : { name: row.name, value_action: "set", value: row.value });
    const submit = async () => {
        if (submitting)
            return;
        setSubmitting(true);
        setError(null);
        try {
            const result = await onSave(toEntries());
            if (result.success) {
                closeModal?.();
            }
            else {
                setError(result.message ?? GENERIC_SAVE_ERROR$1);
            }
        }
        catch {
            setError(GENERIC_SAVE_ERROR$1);
        }
        finally {
            setSubmitting(false);
        }
    };
    const handleNameChange = (id) => (e) => updateRow(id, { name: e.target.value });
    const handleValueChange = (id) => (e) => updateRow(id, { value: e.target.value });
    return (SP_JSX.jsxs(ValidatingModalShell, { ...(closeModal === undefined ? {} : { closeModal }), title: "Custom headers", error: error, errorTestId: "custom-headers-error", submitLabel: submitting ? "Saving…" : "Save", submitDisabled: submitting, onSubmit: () => {
            void submit();
        }, children: [SP_JSX.jsx("div", { style: helperTextStyle$1, children: "Extra headers sent with every request to your RomM server \u2014 for a server behind a proxy that authenticates requests itself. They never go anywhere else. Authorization is not available: it already carries your RomM API token." }), rows.length === 0 && SP_JSX.jsx("div", { style: emptyStyle, children: "No custom headers." }), rows.map((row) => (SP_JSX.jsxs(DFL.Focusable, { style: rowStyle, "data-testid": `header-row-${row.id}`, children: [SP_JSX.jsx(DFL.TextField, { label: "Header name", value: row.name, onChange: handleNameChange(row.id) }), SP_JSX.jsx(DFL.TextField, { label: "Value", ...(keepsStoredValue(row) ? { description: STORED_VALUE_HINT, ...storedValuePlaceholder } : {}), value: row.value, bIsPassword: true, onChange: handleValueChange(row.id) }), SP_JSX.jsx(DFL.DialogButton, { style: removeButtonStyle, onClick: () => removeRow(row.id), children: "Remove" })] }, row.id))), SP_JSX.jsx(DFL.DialogButton, { onClick: addRow, children: "Add header" })] }));
};

const SIGN_OUT_CONFIRM_DESCRIPTION = "This only forgets the RomM token on this device. The token itself stays valid in RomM — " +
    "revoke it there (Settings → API Tokens) if you no longer want it.";
const ConnectionSection = ({ url, hasToken, allowInsecureSsl, status, customHeaderNames, onUrlChange, onSaveCustomHeaders, onConnect, onConnectToken, onConnectPairing, onAllowInsecureSslChange, onSignOut, }) => {
    return (SP_JSX.jsxs(DFL.PanelSection, { title: "RomM", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "RomM URL", description: url || "(not set)", children: SP_JSX.jsx(DFL.DialogButton, { style: { minWidth: "auto", width: "auto" }, onClick: () => DFL.showModal(SP_JSX.jsx(TextInputModal, { label: "RomM URL", value: url, field: "url", onSubmit: onUrlChange })), children: "Edit" }) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Custom headers", description: customHeaderNames.length > 0 ? `${customHeaderNames.length} set` : "(none)", children: SP_JSX.jsx(DFL.DialogButton, { style: { minWidth: "auto", width: "auto" }, onClick: () => DFL.showModal(SP_JSX.jsx(CustomHeadersModal, { storedNames: customHeaderNames, onSave: onSaveCustomHeaders })), children: "Edit" }) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "RomM Account", description: hasToken ? "Signed in" : "Not signed in", children: SP_JSX.jsx(DFL.DialogButton, { style: { minWidth: "auto", width: "auto" }, onClick: () => DFL.showModal(SP_JSX.jsx(ConnectModal, { onConnect: onConnect, onConnectToken: onConnectToken, onConnectPairing: onConnectPairing })), children: hasToken ? "Sign in again" : "Sign in" }) }) }), hasToken && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", description: "Forgets the RomM token on this device. The token stays valid in RomM.", onClick: () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Sign out of RomM?", strDescription: SIGN_OUT_CONFIRM_DESCRIPTION, strOKButtonText: "Sign out", strCancelButtonText: "Cancel", onOK: onSignOut })), children: "Sign out" }) })), isHttpsUrl(url) && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: "Allow Insecure SSL", description: "Skip certificate verification for self-signed certs (LAN only)", checked: allowInsecureSsl, onChange: onAllowInsecureSslChange }) })), status && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: status, focusable: true }) }))] }));
};

const helperTextStyle = { fontSize: "12px", marginBottom: "12px", color: "rgba(255,255,255,0.6)" };
const GENERIC_VERIFY_ERROR = "Could not verify the key. Check your connection and try again.";
const GENERIC_SAVE_ERROR = "The key is valid, but saving it failed. Check your connection and try again.";
const SgdbApiKeyModal = ({ closeModal, onVerify, onSave }) => {
    const [value, setValue] = SP_REACT.useState("");
    const [submitting, setSubmitting] = SP_REACT.useState(false);
    const [error, setError] = SP_REACT.useState(null);
    const canSubmit = value.trim() !== "";
    const submit = async () => {
        if (!canSubmit || submitting)
            return;
        setSubmitting(true);
        setError(null);
        try {
            let check;
            try {
                check = await onVerify(value);
            }
            catch {
                setError(GENERIC_VERIFY_ERROR);
                return;
            }
            if (!check.success) {
                setError(check.message);
                return;
            }
            try {
                await onSave(value);
            }
            catch {
                setError(GENERIC_SAVE_ERROR);
                return;
            }
            closeModal?.();
        }
        finally {
            setSubmitting(false);
        }
    };
    const handleChange = (e) => {
        setValue(e.target.value);
        setError(null);
    };
    const handleKeyDown = (e) => {
        if (e.key !== "Enter")
            return;
        e.preventDefault();
        e.stopPropagation();
        if (canSubmit)
            void submit();
    };
    return (SP_JSX.jsxs(ValidatingModalShell, { ...(closeModal === undefined ? {} : { closeModal }), title: "SteamGridDB API Key", error: error, errorTestId: "sgdb-key-error", submitLabel: submitting ? "Verifying…" : "Save", submitDisabled: !canSubmit || submitting, onSubmit: () => {
            void submit();
        }, children: [SP_JSX.jsx("div", { style: helperTextStyle, children: "Paste the key from your SteamGridDB profile (Preferences \u2192 API). It is checked against SteamGridDB before it is saved." }), SP_JSX.jsx(DFL.Focusable, { children: SP_JSX.jsx(DFL.TextField, { focusOnMount: true, label: "API Key", value: value, bIsPassword: true, onChange: handleChange, onKeyDown: handleKeyDown }) })] }));
};

const SteamGridDBSection = ({ sgdbApiKey, onVerifyKey, onSaveKey }) => {
    return (SP_JSX.jsx(DFL.PanelSection, { title: "SteamGridDB", children: SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "API Key", description: sgdbApiKey ? "••••" : "Not configured", children: SP_JSX.jsx(DFL.DialogButton, { style: { minWidth: "auto", width: "auto" }, onClick: () => DFL.showModal(SP_JSX.jsx(SgdbApiKeyModal, { onVerify: onVerifyKey, onSave: onSaveKey })), children: "Edit" }) }) }) }));
};

const SaveSyncSection = ({ saveSyncSettings, saveSyncToggleKey, deviceInfo, syncing, syncStatus, onToggleSaveSync, onSettingChange, onDefaultSlotSubmit, onResetDefaultSlot, onSyncAll, }) => {
    const saveSyncEnabled = saveSyncSettings?.save_sync_enabled ?? false;
    return (SP_JSX.jsx(DFL.PanelSection, { title: "Save Sync", children: saveSyncSettings ? (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: "Enable Save Sync", description: "Sync RetroArch saves between this device and RomM server", checked: saveSyncEnabled, onChange: onToggleSaveSync }, saveSyncToggleKey) }), !saveSyncEnabled && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Save sync is disabled", description: "Enable above to configure sync settings" }) })), saveSyncEnabled && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [deviceInfo && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Device", description: `Registered as "${deviceInfo.device_name}"`, focusable: true }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: "Sync before launch", description: "Download newer saves from server before starting a game", checked: saveSyncSettings.sync_before_launch, onChange: (value) => onSettingChange({ sync_before_launch: value }) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: "Sync after exit", description: "Upload changed saves to server after closing a game", checked: saveSyncSettings.sync_after_exit, onChange: (value) => onSettingChange({ sync_after_exit: value }) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Default Save Slot", description: `${saveSyncSettings.default_slot} — applies to new games and games without a per-game slot override`, children: SP_JSX.jsx(DFL.DialogButton, { style: { minWidth: "auto", width: "auto" }, onClick: () => DFL.showModal(SP_JSX.jsx(TextInputModal, { label: "Default Save Slot", value: saveSyncSettings.default_slot, onSubmit: onDefaultSlotSubmit })), children: "Edit" }) }) }), saveSyncSettings.default_slot !== "default" && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: onResetDefaultSlot, children: "Reset to default" }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.DropdownItem, { label: "Save History Limit", description: "Max save versions kept per slot on the server", rgOptions: [
                                    { data: 5, label: "5" },
                                    { data: 10, label: "10 (Default)" },
                                    { data: 20, label: "20" },
                                    { data: 50, label: "50" },
                                ], selectedOption: saveSyncSettings.autocleanup_limit, onChange: (option) => onSettingChange({ autocleanup_limit: option.data }) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: onSyncAll, disabled: syncing, children: syncing ? "Syncing..." : "Sync All Saves Now" }) }), syncStatus && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: syncStatus, focusable: true }) }))] }))] })) : (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Loading..." }) })) }));
};

const TABLE_COLUMNS$1 = "1fr 144px 72px";
const TABULAR = { fontVariantNumeric: "tabular-nums" };
const SECONDARY_CELL = { color: MUTED, fontSize: SECONDARY_FONT, ...TABULAR };
const DeviceRow = ({ device }) => {
    const name = device.name ?? "(unnamed)";
    const client = `${device.client ?? "unknown client"} v${device.client_version ?? "?"}`;
    const lastSeen = formatRelativeTime(device.last_seen);
    return (SP_JSX.jsx(PaneTableRow, { columns: TABLE_COLUMNS$1, testId: "device-row", cells: [
            {
                content: (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("span", { style: { flex: "1 1 auto", ...CELL_CLIP }, children: name }), device.is_current_device && (SP_JSX.jsx("span", { style: { flexShrink: 0, color: "#6ab04c", fontSize: SECONDARY_FONT }, children: "(this device)" }))] })),
                style: { display: "flex", alignItems: "center", gap: "8px" },
                title: name,
            },
            { content: client, style: SECONDARY_CELL, title: client },
            { content: lastSeen, style: SECONDARY_CELL, title: lastSeen },
        ] }));
};
const RegisteredDevicesSection = ({ devicesLoading, devicesError, registeredDevices, }) => {
    const devices = devicesLoading || devicesError ? null : registeredDevices;
    return (SP_JSX.jsxs(DFL.PanelSection, { title: "Registered Devices", children: [devicesLoading && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Loading...", focusable: true }) })), !devicesLoading && devicesError && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Could not load devices", description: devicesError, focusable: true }) })), devices !== null && devices.length === 0 && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "No devices registered", focusable: true }) })), devices !== null && devices.length > 0 && (SP_JSX.jsx(PaneTableHeader, { columns: TABLE_COLUMNS$1, cells: ["Device", "Client", "Last seen"], testId: "devices-header" })), devices?.map((device, i) => (SP_JSX.jsx(DeviceRow, { device: device }, device.id || `idx-${i}`)))] }));
};

const FIX_INPUT_DRIVER_DESCRIPTION = "This will change input_driver to sdl2 in your RetroArch config. " +
    "Controllers should work better in RetroArch menus after this change.";
const ControllerSection = ({ steamInputMode, steamInputStatus, retroarchWarning, retroarchFixStatus, applying, onModeChange, onApplyMode, onFixInputDriver, }) => {
    return (SP_JSX.jsxs(DFL.PanelSection, { title: "Controller", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.DropdownItem, { label: "Steam Input Mode", description: "Controls how Steam handles controller input for ROM shortcuts", rgOptions: [
                        { data: "default", label: "Default (Recommended)" },
                        { data: "force_on", label: "Force On" },
                        { data: "force_off", label: "Force Off" },
                    ], selectedOption: steamInputMode, onChange: (option) => onModeChange(option.data) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: onApplyMode, disabled: applying, children: applying ? "Applying to all shortcuts…" : "Apply to All Shortcuts" }) }), steamInputStatus && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: steamInputStatus, focusable: true }) })), retroarchWarning?.warning && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: `RetroArch input_driver: "${retroarchWarning.current}"`, description: "Controller navigation in RetroArch menus may not work with this setting.", focusable: true }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Fix RetroArch input_driver?", strDescription: FIX_INPUT_DRIVER_DESCRIPTION, strOKButtonText: "Apply Fix", strCancelButtonText: "Cancel", onOK: onFixInputDriver })), children: "Fix input_driver to sdl2" }) }), retroarchFixStatus && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: retroarchFixStatus, focusable: true }) }))] }))] }));
};

const AdvancedSection = ({ logLevel, onLogLevelChange }) => {
    const [url, setUrl] = SP_REACT.useState("");
    const [busy, setBusy] = SP_REACT.useState(false);
    const runUpdate = async () => {
        const target = url.trim();
        if (!target || busy) {
            return;
        }
        setBusy(true);
        try {
            const result = await updatePlugin(target);
            toaster.toast({
                title: result.success ? "Updating Arcoon Deck" : "Update refused",
                body: result.message,
            });
        }
        catch (error) {
            toaster.toast({ title: "Update failed", body: String(error) });
        }
        finally {
            setBusy(false);
        }
    };
    return (SP_JSX.jsxs(DFL.PanelSection, { title: "Advanced", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.DropdownItem, { label: "Log Level", description: "Controls how much detail is written to plugin logs", rgOptions: [
                        { data: "error", label: "Error" },
                        { data: "warn", label: "Warn" },
                        { data: "info", label: "Info" },
                        { data: "debug", label: "Debug" },
                    ], selectedOption: logLevel, onChange: (option) => onLogLevelChange(option.data) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.TextField, { label: "Update from URL", description: "A plugin zip built from this repository \u2014 the panel installs it and Decky restarts", value: url, onChange: (event) => setUrl(event.target.value) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Focusable, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", disabled: busy || !url.trim(), onClick: () => { void runUpdate(); }, children: busy ? "Updating…" : "Update now" }) }) })] }));
};

const RUNTIME_CHOICES = [
    { id: "builtin", label: "Built-in" },
    { id: "retrodeck", label: "RetroDECK" },
    { id: "auto", label: "Follow what's installed" },
];
const STRUCTURE_CHOICES = [
    { id: "app", label: "App folder" },
    { id: "emudeck", label: "EmuDeck tree" },
    { id: "retroarch", label: "RetroArch folders" },
    { id: "custom", label: "Custom paths" },
];
const CoreSetupSection = ({ busy, status, onInstall, onAddEmulatorShortcuts, shortcutsBusy, shortcutStatus, runtimeMode, onRuntimeChange, structure, onStructureChange, }) => (SP_JSX.jsxs(DFL.PanelSection, { title: "Emulators & Cores", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#8f98a0", padding: "0 0 6px" }, children: "Runtime \u2014 the app installs and launches its own RetroArch, so its saves are the ones it can answer for. RetroDECK is a fallback you choose, never a requirement." }) }), RUNTIME_CHOICES.map(({ id, label }) => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: () => onRuntimeChange(id), disabled: runtimeMode === id, children: runtimeMode === id ? `${label} — in use` : label }) }, id))), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#8f98a0", padding: "0 0 6px" }, children: "Storage \u2014 where the built-in runtime keeps the ROMs, saves, states and BIOS it manages. Changing it affects what is downloaded or launched next; nothing already on disk is moved." }) }), STRUCTURE_CHOICES.map(({ id, label }) => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: () => onStructureChange(id), disabled: structure === id, children: structure === id ? `${label} — in use` : label }) }, id))), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: onInstall, disabled: busy, children: busy ? "Installing cores…" : "Install Missing Cores" }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#8f98a0", padding: "0 0 6px" }, children: "Downloads the RetroArch runtime and the cores your enabled platforms launch with, then verifies each one. Standalone emulators are not covered yet." }) }), status !== "" && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { style: { fontSize: "12px", color: "#dcdedf" }, children: status }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: onAddEmulatorShortcuts, disabled: shortcutsBusy, children: shortcutsBusy ? "Adding emulators to Steam…" : "Add Emulators to Steam" }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { style: { fontSize: "11px", color: "#8f98a0", padding: "0 0 6px" }, children: "Puts every emulator installed on this Deck into a Steam collection, one tile each, so it can be opened for its own settings or to test a build \u2014 no ROM needed. Emulators installed later are added by the next run." }) }), shortcutStatus !== "" && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { style: { fontSize: "12px", color: "#dcdedf" }, children: shortcutStatus }) }))] }));

let _hostname = "";
async function getHostname() {
    if (_hostname)
        return _hostname;
    try {
        const info = await SteamClient.System.GetSystemInfo();
        _hostname = info.sHostname || "unknown";
    }
    catch {
        _hostname = "unknown";
    }
    return _hostname;
}
function readUserCollections() {
    const store = collectionStore;
    try {
        if (!store || store.deckDesktopApps == null)
            return null;
        return store.userCollections ?? [];
    }
    catch (e) {
        logWarn(`Steam's collection store could not be read: ${e}`);
        return null;
    }
}
function getOverviews(appIds) {
    const overviews = [];
    for (const appId of appIds) {
        if (typeof appStore !== "undefined") {
            const overview = appStore.GetAppOverviewByAppID(appId);
            if (overview) {
                overviews.push(overview);
                continue;
            }
        }
        overviews.push({ appid: appId, display_name: "", strDisplayName: "" });
    }
    return overviews;
}
async function replaceCollectionApps(existing, overviews, signal) {
    const existingApps = existing.allApps;
    if (existingApps.length > 0) {
        if (signal?.aborted)
            return false;
        existing.AsDragDropCollection().RemoveApps(existingApps);
    }
    if (signal?.aborted)
        return false;
    existing.AsDragDropCollection().AddApps(overviews);
    if (signal?.aborted)
        return false;
    await existing.Save();
    return true;
}
async function createCollectionWithApps(collectionName, overviews, signal) {
    const collection = collectionStore.NewUnsavedCollection(collectionName, undefined, []);
    if (signal?.aborted)
        return false;
    collection.AsDragDropCollection().AddApps(overviews);
    if (signal?.aborted)
        return false;
    await collection.Save();
    return true;
}
async function saveCollection(collectionName, noun, overviews, appCount, signal) {
    const collections = readUserCollections();
    if (collections === null) {
        logWarn(`Steam's collections are not readable on this client; leaving "${collectionName}" alone`);
        return false;
    }
    const target = collectionName.toLowerCase();
    const existing = collections.find((c) => c.displayName.toLowerCase() === target);
    if (existing) {
        logInfo(`Updating ${noun} "${collectionName}" with ${appCount} apps`);
        if (!(await replaceCollectionApps(existing, overviews, signal)))
            return false;
    }
    else {
        logInfo(`Creating ${noun} "${collectionName}" with ${appCount} apps`);
        if (!(await createCollectionWithApps(collectionName, overviews, signal)))
            return false;
    }
    logInfo(`Successfully saved ${noun} "${collectionName}"`);
    return true;
}
async function saveCollectionFamily(entries, noun, collectionNameFor, onProgress, signal) {
    for (const [source, appIds] of entries) {
        if (signal?.aborted)
            return;
        const collectionName = collectionNameFor(source);
        const overviews = getOverviews(appIds);
        try {
            if (!(await saveCollection(collectionName, noun, overviews, appIds.length, signal)))
                return;
        }
        catch (colErr) {
            logError(`Failed to save ${noun} "${collectionName}": ${colErr}`);
        }
    }
}
async function createOrUpdateCollections(platformAppIds, onProgress, signal) {
    try {
        if (typeof collectionStore === "undefined") {
            logWarn("collectionStore not available, skipping collections");
            return;
        }
        const hostname = await getHostname();
        if (signal?.aborted)
            return;
        logInfo(`Creating/updating collections for platforms: ${Object.keys(platformAppIds).join(", ")} (hostname: ${hostname})`);
        await saveCollectionFamily(Object.entries(platformAppIds), "collection", (platformName) => `RomM: ${platformName} (${hostname})`, onProgress, signal);
    }
    catch (e) {
        logError(`Failed to update collections: ${e}`);
    }
}
async function createOrUpdateRomMCollections(collectionAppIds, onProgress, signal) {
    try {
        if (typeof collectionStore === "undefined") {
            logWarn("collectionStore not available, skipping RomM collections");
            return;
        }
        const hostname = await getHostname();
        if (signal?.aborted)
            return;
        logInfo(`Creating/updating RomM collections: ${Object.keys(collectionAppIds).join(", ")} (hostname: ${hostname})`);
        await saveCollectionFamily(Object.entries(collectionAppIds), "RomM collection", (collName) => `RomM: [${collName}] (${hostname})`, onProgress, signal);
    }
    catch (e) {
        logError(`Failed to update RomM collections: ${e}`);
    }
}
async function createOrUpdateEmulatorCollection(collectionName, appIds) {
    try {
        if (typeof collectionStore === "undefined") {
            logWarn("collectionStore not available, skipping the emulator collection");
            return;
        }
        const hostname = await getHostname();
        const scopedName = `RomM: ${collectionName} (${hostname})`;
        await saveCollection(scopedName, "emulator collection", getOverviews(appIds), appIds.length);
    }
    catch (e) {
        logError(`Failed to update the emulator collection: ${e}`);
    }
}
async function clearPlatformCollection(platformName, signal) {
    try {
        const collections = readUserCollections();
        if (collections === null) {
            logWarn("Steam's collections are not readable on this client, cannot clear platform collection");
            return;
        }
        const hostname = await getHostname();
        if (signal?.aborted)
            return;
        const scopedName = `RomM: ${platformName} (${hostname})`;
        const legacyName = `RomM: ${platformName}`;
        const scopedTarget = scopedName.toLowerCase();
        const legacyTarget = legacyName.toLowerCase();
        const scoped = collections.find((c) => c.displayName.toLowerCase() === scopedTarget);
        if (scoped) {
            logInfo(`Deleting collection "${scopedName}" (id=${scoped.id})`);
            if (signal?.aborted)
                return;
            await scoped.Delete();
        }
        const legacy = collections.find((c) => c.displayName.toLowerCase() === legacyTarget);
        if (legacy) {
            logInfo(`Deleting legacy collection "${legacyName}" (id=${legacy.id})`);
            if (signal?.aborted)
                return;
            await legacy.Delete();
        }
        if (!scoped && !legacy) {
            logInfo(`Collection "${scopedName}" not found, nothing to clear`);
        }
    }
    catch (e) {
        logError(`Failed to clear platform collection: ${e}`);
    }
}
async function clearAllRomMCollections(signal) {
    try {
        const collections = readUserCollections();
        if (collections === null) {
            logWarn("Steam's collections are not readable on this client, cannot clear collections");
            return;
        }
        const hostname = await getHostname();
        if (signal?.aborted)
            return;
        const suffix = ` (${hostname})`;
        const lowerSuffix = suffix.toLowerCase();
        const rommCollections = collections.filter((c) => {
            const lower = c.displayName.toLowerCase();
            if (!lower.startsWith("romm: "))
                return false;
            if (lower.endsWith(lowerSuffix))
                return true;
            if (!/\s\([^)]+\)$/.test(c.displayName))
                return true;
            return false;
        });
        logInfo(`Deleting ${rommCollections.length} RomM collections (hostname: ${hostname})`);
        for (const c of rommCollections) {
            if (signal?.aborted)
                return;
            logInfo(`Deleting collection "${c.displayName}" (id=${c.id})`);
            await c.Delete();
        }
    }
    catch (e) {
        logError(`Failed to clear collections: ${e}`);
    }
}

function liveShortcutAppIds() {
    if (typeof collectionStore === "undefined")
        return null;
    try {
        const apps = collectionStore.deckDesktopApps?.apps;
        return apps ? new Set(apps.keys()) : null;
    }
    catch (e) {
        logWarn(`Emulator collection: Steam's shortcut store could not be read: ${e}`);
        return null;
    }
}
async function applyAsset(appId, key, base64, assetType) {
    if (!base64)
        return false;
    try {
        if (assetType === 4) {
            const saved = await saveShortcutIcon(appId, base64);
            if (!saved.success || !saved.icon_path)
                return false;
            SteamClient.Apps.SetShortcutIcon(appId, saved.icon_path);
            return true;
        }
        await SteamClient.Apps.SetCustomArtworkForApp(appId, base64, "png", assetType);
        return true;
    }
    catch (e) {
        logWarn(`Emulator artwork: applying asset ${assetType} to ${key} failed: ${e}`);
        return false;
    }
}
async function applyEmulatorArtwork(row, appId) {
    const answers = await Promise.all([1, 2, 3, 4].map((assetType) => getEmulatorArtwork(row.key, assetType).catch(() => ({ base64: null, no_api_key: false }))));
    if (answers.some((answer) => answer.no_api_key)) {
        logInfo("Emulator artwork: no SteamGridDB key configured, leaving the default tiles");
        return 0;
    }
    let applied = 0;
    for (const [index, answer] of answers.entries()) {
        if (await applyAsset(appId, row.key, answer.base64, index + 1))
            applied++;
    }
    return applied;
}
async function syncEmulatorShortcuts() {
    const catalogue = await getEmulatorShortcuts();
    const live = liveShortcutAppIds();
    const store = live !== null && live.size > 0 ? live : null;
    const appIds = [];
    let added = 0;
    let existing = 0;
    let art = 0;
    for (const row of catalogue.emulators) {
        let appId = row.app_id;
        if (appId !== null && store !== null && !store.has(appId)) {
            logWarn(`Emulator collection: ${row.name}'s shortcut (${appId}) is gone; creating it again`);
            try {
                await forgetEmulatorShortcut(row.key);
            }
            catch (e) {
                logWarn(`Emulator collection: could not clear the stale binding for ${row.key}: ${e}`);
            }
            appId = null;
        }
        if (appId === null) {
            const created = await addShortcut({
                name: row.name,
                exe: row.exe,
                start_dir: row.start_dir,
                launch_options: row.launch_options,
            });
            if (created === null) {
                logError(`Emulator collection: could not create a shortcut for ${row.name}`);
                continue;
            }
            appId = created;
            added++;
            try {
                await bindEmulatorShortcut(row.key, created);
            }
            catch (e) {
                logWarn(`Emulator collection: could not bind ${row.key} to ${created}: ${e}`);
            }
        }
        else {
            existing++;
        }
        art += await applyEmulatorArtwork(row, appId);
        appIds.push(appId);
    }
    if (appIds.length > 0) {
        await createOrUpdateEmulatorCollection(catalogue.collection, appIds);
    }
    logInfo(`Emulator collection "${catalogue.collection}": ${added} added, ${existing} present, ${art} images applied`);
    return { collection: catalogue.collection, added, existing, art, total: appIds.length };
}

const AUTO_REGION = "auto";
const ANCHOR_REGIONS = ["World", "USA", "Europe", "Japan"];
const DEFAULT_REGION_LABEL = "Default (World > USA > Europe)";
function buildRegionOptions(libraryRegions, selected) {
    const options = [
        { data: AUTO_REGION, label: DEFAULT_REGION_LABEL },
        ...ANCHOR_REGIONS.map((r) => ({ data: r, label: r })),
    ];
    const known = new Set([AUTO_REGION, ...ANCHOR_REGIONS]);
    const extras = Array.from(new Set(libraryRegions))
        .filter((r) => r && !known.has(r))
        .sort((a, b) => a.localeCompare(b));
    for (const r of extras) {
        options.push({ data: r, label: r });
        known.add(r);
    }
    if (selected !== AUTO_REGION && !known.has(selected)) {
        options.push({ data: selected, label: selected });
    }
    return options;
}
const LibrarySection = ({ preferredRegion, libraryRegions, onPreferredRegionChange, platformGroups, onPlatformGroupsChange, namingMode, onNamingModeChange, }) => {
    return (SP_JSX.jsxs(DFL.PanelSection, { title: "Steam Library", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.DropdownItem, { label: "Preferred region", description: "When a game has several regional versions, prefer this region for the shortcut and its name. Applies to games synced from now on; existing shortcuts keep their name.", rgOptions: buildRegionOptions(libraryRegions, preferredRegion), selectedOption: preferredRegion, onChange: (option) => onPreferredRegionChange(option.data) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: "Show collection games in platform groups", description: "When syncing a collection, also add its games to their platform-specific Steam group.", checked: platformGroups, onChange: onPlatformGroupsChange }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: "Distinguish collection types in Steam names", description: "Adds the collection type (e.g. Franchise, IGDB Collection) to the Steam collection name so collections that share a name stay separate instead of merging into one. Applies on the next sync.", checked: namingMode === "by_label", onChange: (v) => onNamingModeChange(v ? "by_label" : "merge") }) })] }));
};

const PreferredRegionModalContent = ({ oldLabel, newLabel, closeModal, onDone }) => {
    const handleChoice = (proceed) => {
        closeModal?.();
        onDone(proceed);
    };
    return (SP_JSX.jsx(DFL.ModalRoot, { closeModal: () => {
            closeModal?.();
            onDone(false);
        }, children: SP_JSX.jsxs("div", { style: { padding: "16px", minWidth: "320px" }, children: [SP_JSX.jsx("div", { style: { fontSize: "16px", fontWeight: "bold", marginBottom: "4px", color: "#fff" }, children: "Change Preferred Region" }), SP_JSX.jsxs("div", { style: { fontSize: "13px", color: "rgba(255, 255, 255, 0.6)", marginBottom: "16px" }, children: [oldLabel, " \u2192 ", newLabel] }), SP_JSX.jsx("div", { style: {
                        padding: "10px",
                        background: "rgba(26, 159, 255, 0.12)",
                        borderRadius: "4px",
                        border: "1px solid rgba(26, 159, 255, 0.3)",
                        marginBottom: "12px",
                    }, children: SP_JSX.jsxs("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.8)", lineHeight: "1.4" }, children: ["This applies to games synced ", SP_JSX.jsx("b", { children: "from now on" }), ". When a game has several regional versions, the plugin will prefer this region for the version it binds and the name it gives the new Steam shortcut.", SP_JSX.jsx("br", {}), SP_JSX.jsx("br", {}), "Games you have ", SP_JSX.jsx("b", { children: "already synced keep their current version and shortcut name" }), " \u2014 changing this never switches a game's version or renames an existing shortcut. Run a sync to apply it to new games."] }) }), SP_JSX.jsxs("div", { style: { display: "flex", flexDirection: "column", gap: "8px" }, children: [SP_JSX.jsx(DFL.DialogButton, { onClick: () => handleChoice(true), children: "Save" }), SP_JSX.jsx(DFL.DialogButton, { onClick: () => handleChoice(false), style: { opacity: 0.5 }, children: "Cancel" })] })] }) }));
};
function showPreferredRegionModal(oldLabel, newLabel) {
    return new Promise((resolve) => {
        DFL.showModal(SP_JSX.jsx(PreferredRegionModalContent, { oldLabel: oldLabel, newLabel: newLabel, onDone: resolve }));
    });
}

const INVALID_URL_MESSAGE = "Enter a valid http:// or https:// server URL";
const GENERIC_SIGN_IN_ERROR = "Sign-in failed. Check your connection and try again.";
const SECTION_LABELS = {
    connections: "Connections",
    "save-sync": "Save Sync",
    controller: "Controller",
    "steam-library": "Steam Library",
    cores: "Emulators & Cores",
    advanced: "Advanced",
};
const asSection = (id) => SETTINGS_SECTIONS.find((candidate) => candidate === id) ?? SETTINGS_SECTIONS[0];
const SettingsPage = ({ onBack, section }) => {
    const [selectedSection, setSelectedSection] = SP_REACT.useState(section ?? SETTINGS_SECTIONS[0]);
    const [url, setUrl] = SP_REACT.useState("");
    const [hasToken, setHasToken] = SP_REACT.useState(false);
    const [status, setStatus] = SP_REACT.useState("");
    const [allowInsecureSsl, setAllowInsecureSsl] = SP_REACT.useState(false);
    const [customHeaderNames, setCustomHeaderNames] = SP_REACT.useState([]);
    const [sgdbApiKey, setSgdbApiKey] = SP_REACT.useState("");
    const [saveSyncSettings, setSaveSyncSettings] = SP_REACT.useState(null);
    const [saveSyncToggleKey, setSaveSyncToggleKey] = SP_REACT.useState(0);
    const [deviceInfo, setDeviceInfo] = SP_REACT.useState(null);
    const [syncing, setSyncing] = SP_REACT.useState(false);
    const [syncStatus, setSyncStatus] = SP_REACT.useState("");
    const [registeredDevices, setRegisteredDevices] = SP_REACT.useState(null);
    const [devicesLoading, setDevicesLoading] = SP_REACT.useState(false);
    const [devicesError, setDevicesError] = SP_REACT.useState(null);
    const [steamInputMode, setSteamInputMode] = SP_REACT.useState("default");
    const [steamInputStatus, setSteamInputStatus] = SP_REACT.useState("");
    const [applyingSteamInput, setApplyingSteamInput] = SP_REACT.useState(false);
    const [coresBusy, setCoresBusy] = SP_REACT.useState(false);
    const [shortcutsBusy, setShortcutsBusy] = SP_REACT.useState(false);
    const [shortcutStatus, setShortcutStatus] = SP_REACT.useState("");
    const [coresStatus, setCoresStatus] = SP_REACT.useState("");
    const [retroarchWarning, setRetroarchWarning] = SP_REACT.useState(null);
    const [retroarchFixStatus, setRetroarchFixStatus] = SP_REACT.useState("");
    const saveSortMigration = useSaveSortMigrationState();
    const [saveSortMigrating, setSaveSortMigrating] = SP_REACT.useState(false);
    const [saveSortResult, setSaveSortResult] = SP_REACT.useState("");
    const [logLevel, setLogLevel] = SP_REACT.useState("warn");
    const [runtimeMode, setRuntimeMode] = SP_REACT.useState("builtin");
    const [structure, setStructure] = SP_REACT.useState("app");
    const [preferredRegion, setPreferredRegion] = SP_REACT.useState(AUTO_REGION);
    const [libraryRegions, setLibraryRegions] = SP_REACT.useState([]);
    const [platformGroups, setPlatformGroups] = SP_REACT.useState(false);
    const [namingMode, setNamingMode] = SP_REACT.useState("merge");
    SP_REACT.useEffect(() => {
        getSettings()
            .then((s) => {
            setUrl(pendingEdits.url ?? s.romm_url);
            setHasToken(s.has_token);
            setAllowInsecureSsl(s.romm_allow_insecure_ssl);
            setCustomHeaderNames(s.romm_custom_header_names ?? []);
            setSgdbApiKey(s.sgdb_api_key_masked);
            setSteamInputMode(s.steam_input_mode);
            setLogLevel(s.log_level);
            setRuntimeMode(s.runtime_mode ?? "builtin");
            setStructure(s.structure ?? "app");
            setPreferredRegion(s.preferred_region ?? AUTO_REGION);
            setPlatformGroups(!!s.collection_create_platform_groups);
            setNamingMode(s.collection_naming_mode ?? "merge");
            if (s.retroarch_input_check) {
                setRetroarchWarning(s.retroarch_input_check);
            }
        })
            .catch((e) => {
            logError(`Failed to load settings: ${e}`);
            setStatus("Failed to load settings");
        });
        getKnownRegions()
            .then((regions) => setLibraryRegions(regions))
            .catch(() => { });
        getSaveSyncSettings()
            .then((settings) => {
            setSaveSyncSettings(settings);
            if (settings.save_sync_enabled) {
                ensureDeviceRegistered()
                    .then((result) => {
                    if (result.success) {
                        setDeviceInfo({ device_id: result.device_id, device_name: result.device_name });
                    }
                })
                    .catch(() => { });
                loadDevices();
            }
        })
            .catch((e) => logError(`Failed to load save sync settings: ${e}`));
        getSaveSortMigrationStatus()
            .then((s) => {
            if (s.pending) {
                setSaveSortMigrationStatus(s);
            }
        })
            .catch(() => { });
    }, []);
    function loadDevices() {
        setDevicesLoading(true);
        setDevicesError(null);
        listDevices()
            .then((result) => {
            if (result.success) {
                setRegisteredDevices(result.devices);
            }
            else if (result.disabled) {
                setRegisteredDevices(null);
            }
            else {
                setDevicesError(result.message ?? "Failed to load devices");
                setRegisteredDevices([]);
            }
        })
            .catch((e) => {
            setDevicesError(e instanceof Error ? e.message : "Failed to load devices");
            setRegisteredDevices([]);
        })
            .finally(() => {
            setDevicesLoading(false);
        });
    }
    const handleSaveSyncSettingChange = async (partial) => {
        if (!saveSyncSettings)
            return;
        const updated = { ...saveSyncSettings, ...partial };
        setSaveSyncSettings(updated);
        try {
            await updateSaveSyncSettings(updated);
            if ("save_sync_enabled" in partial) {
                globalThis.dispatchEvent(new CustomEvent("romm_data_changed", {
                    detail: { type: "save_sync_settings", save_sync_enabled: updated.save_sync_enabled },
                }));
                if (updated.save_sync_enabled) {
                    loadDevices();
                }
                else {
                    setRegisteredDevices(null);
                    setDevicesError(null);
                }
            }
        }
        catch (e) {
            logError(`Failed to save settings: ${e}`);
        }
    };
    const handleSyncAll = async () => {
        setSyncing(true);
        setSyncStatus("");
        try {
            const result = await syncAllSaves();
            setSyncStatus(result.message);
            globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "save_sync" } }));
        }
        catch {
            setSyncStatus("Sync failed");
        }
        setSyncing(false);
    };
    const handleEnableSaveSync = () => {
        DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Enable Save Sync?", strDescription: "This will sync your RetroArch game saves between this device and your RomM server. " +
                "Save sync covers the per-game save files RetroArch writes for the systems it supports " +
                "- SRAM, RTC, EEPROM, and other per-system formats, not a single file type. " +
                "Coverage varies by system; see the save sync support matrix in the docs.\n\n" +
                "Before enabling, please back up your local save files. " +
                "They are stored in your RetroArch/RetroDECK saves directory.\n\n" +
                "IMPORTANT: Save sync requires RetroArch's save sorting to be set to " +
                '"Sort Saves into Folders by Content Directory = ON" and ' +
                '"Sort Saves into Folders by Core Name = OFF" (RetroDECK default). ' +
                "If you changed these settings, save sync will not find your save files.\n\n" +
                "Also make sure you are not using this on a shared RomM account " +
                "(e.g. admin, romm, guest) - unless you know what you are doing. " +
                "Save sync is intended for single user accounts.\n\n" +
                "Are you sure you want to proceed?", strOKButtonText: "I am sure", strCancelButtonText: "Cancel", onOK: () => {
                detach(handleSaveSyncSettingChange({ save_sync_enabled: true }));
            }, onCancel: () => {
                setSaveSyncToggleKey((k) => k + 1);
            } }));
    };
    const handleDisableSaveSync = () => {
        detach(handleSaveSyncSettingChange({ save_sync_enabled: false }));
    };
    const handleToggleSaveSync = (value) => {
        if (value) {
            handleEnableSaveSync();
        }
        else {
            handleDisableSaveSync();
        }
    };
    const saveSyncEnabled = saveSyncSettings?.save_sync_enabled ?? false;
    const handleUrlChange = async (value) => {
        const trimmed = trimServerUrl(value);
        setUrl(trimmed);
        try {
            if (!isValidServerUrl(trimmed)) {
                setStatus(INVALID_URL_MESSAGE);
                return;
            }
            await saveServerUrl(trimmed, allowInsecureSsl);
        }
        catch {
            setStatus("Failed to save settings");
        }
        finally {
            delete pendingEdits.url;
        }
    };
    const handleSaveCustomHeaders = async (headers) => {
        const result = await saveCustomHeaders(headers);
        if (result.success) {
            setCustomHeaderNames(headers.map((h) => h.name.trim()));
        }
        return result;
    };
    const handleAllowInsecureSslChange = (val) => {
        setAllowInsecureSsl(val);
        saveServerUrl(url, val).catch(() => {
            setStatus("Failed to save settings");
        });
    };
    const handleConnect = async (username, password) => {
        const trimmed = trimServerUrl(url);
        if (!isValidServerUrl(trimmed)) {
            return { success: false, message: INVALID_URL_MESSAGE };
        }
        try {
            const result = await connectWithCredentials(trimmed, username, password, allowInsecureSsl);
            if (result.success) {
                setHasToken(true);
                setStatus(result.message);
            }
            return result;
        }
        catch {
            return { success: false, message: GENERIC_SIGN_IN_ERROR };
        }
    };
    const handleConnectToken = async (token) => {
        const trimmed = trimServerUrl(url);
        if (!isValidServerUrl(trimmed)) {
            return { success: false, message: INVALID_URL_MESSAGE };
        }
        try {
            const result = await connectWithToken(trimmed, token, allowInsecureSsl);
            if (result.success) {
                setHasToken(true);
                setStatus(result.message);
            }
            return result;
        }
        catch {
            return { success: false, message: GENERIC_SIGN_IN_ERROR };
        }
    };
    const handleConnectPairing = async (code) => {
        const trimmed = trimServerUrl(url);
        if (!isValidServerUrl(trimmed)) {
            return { success: false, message: INVALID_URL_MESSAGE };
        }
        try {
            const result = await connectWithPairingCode(trimmed, code, allowInsecureSsl);
            if (result.success) {
                setHasToken(true);
                setStatus(result.message);
            }
            return result;
        }
        catch {
            return { success: false, message: GENERIC_SIGN_IN_ERROR };
        }
    };
    const handleSignOut = async () => {
        setStatus("");
        try {
            const result = await signOut();
            setStatus(result.message);
            if (result.success) {
                setHasToken(false);
            }
        }
        catch {
            setStatus("Sign-out failed");
        }
    };
    const handleSaveSgdbKey = async (value) => {
        await saveSgdbApiKey(value);
        setSgdbApiKey("set");
    };
    const handleResetDefaultSlot = () => {
        setSaveSyncSettings((prev) => (prev ? { ...prev, default_slot: "default" } : prev));
        detach(handleSaveSyncSettingChange({ default_slot: "default" }));
        showToast('Default save slot reset to "default".');
    };
    const handleDefaultSlotSubmit = (value) => {
        const trimmed = value.trim();
        if (trimmed) {
            setSaveSyncSettings((prev) => (prev ? { ...prev, default_slot: trimmed } : prev));
            detach(handleSaveSyncSettingChange({ default_slot: trimmed }));
        }
        else {
            handleResetDefaultSlot();
        }
    };
    const handleSteamInputModeChange = (mode) => {
        setSteamInputMode(mode);
        detach(saveSteamInputSetting(mode));
        setSteamInputStatus("");
    };
    const handleAddEmulatorShortcuts = async () => {
        setShortcutsBusy(true);
        setShortcutStatus("Looking for the emulators on this Deck…");
        try {
            const outcome = await syncEmulatorShortcuts();
            const images = outcome.art > 0 ? `, ${outcome.art} image${outcome.art === 1 ? "" : "s"} applied` : "";
            if (outcome.total === 0) {
                setShortcutStatus("No emulators found on this Deck yet.");
            }
            else if (outcome.added === 0) {
                setShortcutStatus(`All ${outcome.total} emulators are already in the "${outcome.collection}" collection${images}.`);
            }
            else {
                setShortcutStatus(`Added ${outcome.added} emulator${outcome.added === 1 ? "" : "s"} to the "${outcome.collection}" collection` +
                    `${outcome.existing > 0 ? ` (${outcome.existing} already there)` : ""}${images}.`);
            }
        }
        catch (e) {
            logError(`Failed to add the emulators to Steam: ${e}`);
            setShortcutStatus("Could not add the emulators to Steam. Check the log for the reason.");
        }
        finally {
            setShortcutsBusy(false);
        }
    };
    const handleInstallCores = async () => {
        setCoresBusy(true);
        setCoresStatus("Installing the runtime and the cores your platforms need…");
        try {
            const result = await ensureAllPlatformCores();
            const installed = result.installed ?? [];
            const failed = result.failed ?? [];
            const skipped = result.skipped ?? [];
            const uncovered = skipped.length > 0 ? ` No automatic emulator yet for: ${skipped.join(", ")}.` : "";
            if (failed.length > 0) {
                setCoresStatus(`Installed ${installed.length}, but ${failed.length} failed: ${failed.map((entry) => entry.core).join(", ")}.${uncovered}`);
            }
            else if (installed.length > 0) {
                setCoresStatus(`Installed ${installed.length} core${installed.length === 1 ? "" : "s"}.${uncovered}`);
            }
            else if (skipped.length > 0) {
                setCoresStatus(`Nothing to install for your platforms.${uncovered}`);
            }
            else if (result.runtime?.reason) {
                setCoresStatus(`Could not install the runtime: ${result.runtime.reason}`);
            }
            else {
                setCoresStatus("Everything your platforms need is already installed.");
            }
        }
        catch (error) {
            setCoresStatus(`Install failed: ${String(error)}`);
        }
        finally {
            setCoresBusy(false);
        }
    };
    const handleApplySteamInput = async () => {
        if (applyingSteamInput)
            return;
        setApplyingSteamInput(true);
        setSteamInputStatus("Applying...");
        try {
            const result = await applySteamInputSetting();
            setSteamInputStatus(result.message);
        }
        catch {
            setSteamInputStatus("Failed to apply");
        }
        finally {
            setApplyingSteamInput(false);
        }
    };
    const handleFixInputDriver = async () => {
        setRetroarchFixStatus("Applying...");
        try {
            const result = await fixRetroarchInputDriver();
            setRetroarchFixStatus(result.message);
            if (result.success) {
                setRetroarchWarning(null);
            }
        }
        catch {
            setRetroarchFixStatus("Failed to apply fix");
        }
    };
    const handleRuntimeChange = (mode) => {
        if (mode === runtimeMode)
            return;
        setRuntimeMode(mode);
        detach(saveRuntimeMode(mode));
    };
    const handleStructureChange = (next) => {
        if (next === structure)
            return;
        setStructure(next);
        detach(saveStructure(next));
    };
    const handleLogLevelChange = (level) => {
        setLogLevel(level);
        detach(saveLogLevel(level));
    };
    const regionLabel = (value) => (value === AUTO_REGION ? DEFAULT_REGION_LABEL : value);
    const handlePreferredRegionChange = (region) => {
        if (region === preferredRegion)
            return;
        detach((async () => {
            const proceed = await showPreferredRegionModal(regionLabel(preferredRegion), regionLabel(region));
            if (proceed) {
                setPreferredRegion(region);
                detach(savePreferredRegion(region));
            }
        })());
    };
    const handlePlatformGroupsChange = (value) => {
        setPlatformGroups(value);
        detach((async () => {
            try {
                await saveCollectionPlatformGroups(value);
            }
            catch {
                setPlatformGroups(!value);
            }
        })());
    };
    const handleNamingModeChange = (mode) => {
        const previous = namingMode;
        setNamingMode(mode);
        detach((async () => {
            try {
                await setCollectionNamingMode(mode);
            }
            catch {
                setNamingMode(previous);
            }
        })());
    };
    const handleMigrateSaveSort = async () => {
        setSaveSortMigrating(true);
        setSaveSortResult("");
        try {
            const result = await migrateSaveSortFiles(null);
            setSaveSortResult(result.message);
            if (result.success) {
                clearSaveSortMigration();
                showToast(result.message || "Migration complete.");
            }
        }
        catch {
            setSaveSortResult("Migration failed");
        }
        setSaveSortMigrating(false);
    };
    const handleDismissSaveSort = async () => {
        try {
            await dismissSaveSortMigration();
            clearSaveSortMigration();
        }
        catch {
        }
    };
    const renderSection = (id) => {
        switch (id) {
            case "connections":
                return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(ConnectionSection, { url: url, hasToken: hasToken, allowInsecureSsl: allowInsecureSsl, status: status, customHeaderNames: customHeaderNames, onUrlChange: (value) => {
                                detach(handleUrlChange(value));
                            }, onSaveCustomHeaders: handleSaveCustomHeaders, onConnect: handleConnect, onConnectToken: handleConnectToken, onConnectPairing: handleConnectPairing, onAllowInsecureSslChange: handleAllowInsecureSslChange, onSignOut: () => {
                                detach(handleSignOut());
                            } }), SP_JSX.jsx(SteamGridDBSection, { sgdbApiKey: sgdbApiKey, onVerifyKey: verifySgdbApiKey, onSaveKey: handleSaveSgdbKey })] }));
            case "save-sync":
                return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [saveSortMigration.pending && (SP_JSX.jsx(SaveSortMigrationSection, { migration: saveSortMigration, migrating: saveSortMigrating, result: saveSortResult, onMigrate: () => {
                                detach(handleMigrateSaveSort());
                            }, onDismiss: () => {
                                detach(handleDismissSaveSort());
                            } })), SP_JSX.jsx(SaveSyncSection, { saveSyncSettings: saveSyncSettings, saveSyncToggleKey: saveSyncToggleKey, deviceInfo: deviceInfo, syncing: syncing, syncStatus: syncStatus, onToggleSaveSync: handleToggleSaveSync, onSettingChange: (partial) => {
                                detach(handleSaveSyncSettingChange(partial));
                            }, onDefaultSlotSubmit: handleDefaultSlotSubmit, onResetDefaultSlot: handleResetDefaultSlot, onSyncAll: () => {
                                detach(handleSyncAll());
                            } }), saveSyncEnabled && (devicesLoading || registeredDevices !== null) && (SP_JSX.jsx(RegisteredDevicesSection, { devicesLoading: devicesLoading, devicesError: devicesError, registeredDevices: registeredDevices }))] }));
            case "controller":
                return (SP_JSX.jsx(ControllerSection, { steamInputMode: steamInputMode, steamInputStatus: steamInputStatus, retroarchWarning: retroarchWarning, retroarchFixStatus: retroarchFixStatus, applying: applyingSteamInput, onModeChange: handleSteamInputModeChange, onApplyMode: () => {
                        detach(handleApplySteamInput());
                    }, onFixInputDriver: () => {
                        detach(handleFixInputDriver());
                    } }));
            case "steam-library":
                return (SP_JSX.jsx(LibrarySection, { preferredRegion: preferredRegion, libraryRegions: libraryRegions, onPreferredRegionChange: handlePreferredRegionChange, platformGroups: platformGroups, onPlatformGroupsChange: handlePlatformGroupsChange, namingMode: namingMode, onNamingModeChange: handleNamingModeChange }));
            case "cores":
                return (SP_JSX.jsx(CoreSetupSection, { busy: coresBusy, status: coresStatus, runtimeMode: runtimeMode, onRuntimeChange: handleRuntimeChange, structure: structure, onStructureChange: handleStructureChange, onInstall: () => {
                        detach(handleInstallCores());
                    }, onAddEmulatorShortcuts: () => {
                        detach(handleAddEmulatorShortcuts());
                    }, shortcutsBusy: shortcutsBusy, shortcutStatus: shortcutStatus }));
            case "advanced":
                return SP_JSX.jsx(AdvancedSection, { logLevel: logLevel, onLogLevelChange: handleLogLevelChange });
        }
    };
    const items = SETTINGS_SECTIONS.map((id) => ({
        id,
        render: (selected) => (SP_JSX.jsx("div", { "data-testid": `settings-section-${id}`, style: {
                borderLeft: `${ROW_MARKER_WIDTH}px solid ${selected ? SELECTION_ACCENT : "transparent"}`,
                paddingLeft: `${ROW_MARKER_GAP}px`,
            }, children: SP_JSX.jsx(DFL.Field, { label: SECTION_LABELS[id], bottomSeparator: "none" }) })),
    }));
    return (SP_JSX.jsx(WidePage, { title: "Settings", onBack: onBack, ownRegions: true, children: SP_JSX.jsx(ListDetail, { items: items, selectedId: selectedSection, onSelect: (id) => setSelectedSection(asSection(id)), selectOnActivate: true, renderDetail: (id) => renderSection(asSection(id)) }) }));
};

function fuzzyMatch(query, target) {
    const q = query.toLowerCase();
    const t = target.toLowerCase();
    let qi = 0;
    for (let ti = 0; ti < t.length && qi < q.length; ti++) {
        if (t[ti] === q[qi])
            qi++;
    }
    return qi === q.length;
}

const LOADING_SPINNER_SIZE = 24;
const LoadingRow = ({ label }) => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs("div", { style: { display: "flex", alignItems: "center", justifyContent: "center", gap: "8px", padding: "8px 0" }, children: [SP_JSX.jsx(DFL.Spinner, { width: LOADING_SPINNER_SIZE, height: LOADING_SPINNER_SIZE }), label ? SP_JSX.jsx("span", { style: { fontSize: "13px", opacity: 0.7 }, children: label }) : null] }) }));

const SYNC_RUNNING_HINT = "Unavailable while a library sync is running.";
const useSyncRunning = () => {
    const [syncRunning, setSyncRunning] = SP_REACT.useState(getSyncProgress().running);
    SP_REACT.useEffect(() => onSyncProgressChange(() => setSyncRunning(getSyncProgress().running)), []);
    return syncRunning;
};

const REASON_TEXT = {
    no_digest: "the release publishes no hash to check the download against",
    hash_mismatch: "the download did not match the hash its release publishes",
    asset_unresolved: "the release does not attach exactly one Linux build",
    release_unreachable: "the project's release could not be read",
    no_install_path: "the inventory names no place to install it",
    no_source: "the inventory states no source for it",
};
const reasonText = (reason) => {
    const [code = ""] = reason.split(":", 1);
    const known = REASON_TEXT[code];
    if (known)
        return known;
    const detail = reason.includes(":") ? reason.slice(reason.indexOf(":") + 1).trim() : reason;
    return detail || "it could not be installed";
};
const sourceText = (row) => row.source === "store" ? "flatpak store" : row.source === "release" ? "release build" : "no source";
const StatusLine = ({ row, state }) => {
    if (state.kind === "running") {
        return (SP_JSX.jsxs("span", { style: { display: "inline-flex", alignItems: "center", gap: "6px", fontSize: SECONDARY_FONT, color: MUTED }, children: [SP_JSX.jsx(DFL.Spinner, { width: 10, height: 10 }), `Installing ${row.label}…`] }));
    }
    if (state.kind === "installed") {
        const suffix = state.version ? ` ${state.version}` : "";
        return SP_JSX.jsx("span", { style: { fontSize: SECONDARY_FONT, color: GREEN }, children: `Installed ${row.label}${suffix}` });
    }
    if (state.kind === "present") {
        return SP_JSX.jsx("span", { style: { fontSize: SECONDARY_FONT, color: GREEN }, children: `${row.label} is already installed` });
    }
    if (state.kind === "failed") {
        return SP_JSX.jsx("span", { style: { fontSize: SECONDARY_FONT, color: RED }, children: `${row.label}: ${reasonText(state.reason)}` });
    }
    return SP_JSX.jsx("span", { style: { fontSize: SECONDARY_FONT, color: MUTED }, children: `${row.label} · ${sourceText(row)}` });
};
const EmulatorInstallSection = ({ slug }) => {
    const [rows, setRows] = SP_REACT.useState(null);
    const [manual, setManual] = SP_REACT.useState([]);
    const [readFailed, setReadFailed] = SP_REACT.useState(false);
    const [rowsState, setRowsState] = SP_REACT.useState({});
    const [running, setRunning] = SP_REACT.useState(false);
    SP_REACT.useEffect(() => {
        let live = true;
        setRows(null);
        setManual([]);
        setReadFailed(false);
        setRowsState({});
        Promise.resolve()
            .then(() => getPlatformEmulators(slug))
            .then((answer) => {
            if (!live)
                return;
            setRows(answer.emulators);
            setManual(answer.manual);
        })
            .catch((error) => {
            if (!live)
                return;
            logWarn(`Failed to read the installable emulators for ${slug}: ${String(error)}`);
            setReadFailed(true);
        });
        return () => {
            live = false;
        };
    }, [slug]);
    const install = SP_REACT.useCallback(async () => {
        if (!rows || rows.length === 0)
            return;
        setRunning(true);
        for (const row of rows) {
            setRowsState((prev) => ({ ...prev, [row.label]: { kind: "running" } }));
            try {
                const result = await ensurePlatformEmulator(slug, row.label);
                setRowsState((prev) => ({
                    ...prev,
                    [row.label]: result.ok
                        ? result.already_present
                            ? { kind: "present" }
                            : { kind: "installed", version: result.version ?? null }
                        : { kind: "failed", reason: result.reason ?? "it could not be installed" },
                }));
            }
            catch (error) {
                logWarn(`Installing ${row.label} for ${slug} failed: ${String(error)}`);
                setRowsState((prev) => ({ ...prev, [row.label]: { kind: "failed", reason: String(error) } }));
            }
        }
        setRunning(false);
    }, [rows, slug]);
    if (!readFailed && rows !== null && rows.length === 0 && manual.length === 0)
        return null;
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(SectionTitle, { title: "Standalone emulators" }), readFailed && (SP_JSX.jsx(Muted, { children: "Could not read which emulators this platform can install. Reopen the platform to try again." })), rows?.map((row) => (SP_JSX.jsx("div", { style: { padding: "2px 16px" }, children: SP_JSX.jsx(StatusLine, { row: row, state: rowsState[row.label] ?? { kind: "idle" } }) }, row.label))), manual.length > 0 && (SP_JSX.jsx("div", { style: { padding: "2px 16px", fontSize: SECONDARY_FONT, color: MUTED }, children: `Install by hand — the plugin has no source for ${manual.join(", ")}` })), rows !== null && rows.length > 0 && (SP_JSX.jsx("div", { style: { display: "flex", padding: "6px 16px 2px" }, children: SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: running, onClick: () => {
                        void install();
                    }, children: SP_JSX.jsxs("span", { style: { display: "inline-flex", alignItems: "center", gap: "6px", fontSize: "13px" }, children: [running && SP_JSX.jsx(DFL.Spinner, { width: 12, height: 12 }), rows.length > 1 ? "Install emulators" : "Install emulator"] }) }) }))] }));
};

const scopedStatus = (status) => status && { key: status.slug, scope: status.scope, text: status.text };
const LIBRARY_MARK = { glyph: "⊘", color: VIOLET, title: "not in your RomM library" };
const MARK_REQUIRED_MISSING = "required, missing";
const MARK_REQUIRED_HERE = "required, here";
const MARK_HERE = "here, not required";
const MARK_MISSING = "missing, not required";
const MARK_UNCHECKED = "nothing could establish this either way";
const MARK_HERE_NEED_UNKNOWN = "here; nothing could say whether this is wanted";
const MARK_MISSING_NEED_UNKNOWN = "missing; nothing could say whether this is wanted";
const MARK_STARTS_THE_SYSTEM = "this starts the system";
const MARK_ONE_OF_THESE_MISSING = "one of these — any one starts the system";
const MARK_ONE_OF_THESE_SPARE = "not needed — one of these is already in place";
const MARK_ONE_OF_THESE_UNSETTLED = "one of these — whether one is in place could not be checked";
const CORE_BUTTON = {
    alignSelf: "center",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: "28px",
    minWidth: "28px",
    height: "28px",
    padding: 0,
    borderRadius: "4px",
    flexShrink: 0,
};
function diskMark(file, systemImage) {
    const verdict = rowVerdict(file);
    if (verdict === null)
        return { glyph: "?", color: AMBER, title: MARK_UNCHECKED };
    const needUnknown = file.wanted === "unknown";
    const required = file.required_by_active;
    const candidate = file.system_image_candidate === true;
    if (verdict) {
        if (needUnknown)
            return { glyph: "✓", color: AMBER, title: MARK_HERE_NEED_UNKNOWN };
        if (candidate)
            return systemImageCandidateMark(verdict, systemImage);
        return { glyph: "✓", color: required ? GREEN : PALE_GREEN, title: required ? MARK_REQUIRED_HERE : MARK_HERE };
    }
    if (needUnknown)
        return { glyph: "✗", color: AMBER, title: MARK_MISSING_NEED_UNKNOWN };
    if (candidate)
        return systemImageCandidateMark(verdict, systemImage);
    return { glyph: "✗", color: required ? RED : MUTED, title: required ? MARK_REQUIRED_MISSING : MARK_MISSING };
}
function rowVerdict(file) {
    const declaredFolder = file.declared_kind === "directory";
    const fallback = declaredFolder ? null : file.downloaded;
    return file.satisfied !== undefined ? file.satisfied : fallback;
}
function systemImageCandidateMark(verdict, systemImage) {
    if (verdict)
        return { glyph: "✓", color: GREEN, title: MARK_STARTS_THE_SYSTEM };
    if (systemImage === "absent")
        return { glyph: "✗", color: RED, title: MARK_ONE_OF_THESE_MISSING };
    if (systemImage === "held")
        return { glyph: "✗", color: MUTED, title: MARK_ONE_OF_THESE_SPARE };
    return { glyph: "✗", color: AMBER, title: MARK_ONE_OF_THESE_UNSETTLED };
}
function libraryMark(file) {
    return file.on_server === false && file.declared_kind !== "directory" ? LIBRARY_MARK : null;
}
const TABLE_COLUMNS = "1fr 48px 84px 92px";
const BiosTableHeader = () => (SP_JSX.jsx(PaneTableHeader, { columns: TABLE_COLUMNS, cells: ["File", "On disk", "Contents", ""] }));
function contentsCell(file) {
    if (file.declared_kind !== "directory")
        return "—";
    if (file.satisfied === true) {
        const held = file.images?.length ?? 0;
        if (held === 0)
            return "an image";
        return held === 1 ? "1 image" : `${held} images`;
    }
    return file.satisfied === false ? "no image" : "unknown";
}
const BiosRowLines = ({ lines }) => lines.length === 0 ? null : (SP_JSX.jsx("div", { style: { display: "flex", flexDirection: "column", gap: "2px", marginLeft: "18px", marginTop: "2px" }, children: lines.map((line) => (SP_JSX.jsx("div", { style: { fontSize: SECONDARY_FONT, color: MUTED, whiteSpace: "pre-wrap" }, children: line }, line))) }));
function declaredFolder(file) {
    const declared = file.declared_path;
    if (!declared?.includes("/"))
        return null;
    return `${declared.slice(0, declared.lastIndexOf("/"))}/`;
}
const BiosLegend = ({ files, systemImage }) => {
    const marks = files.map((file) => diskMark(file, systemImage));
    const shown = [
        { glyph: "✗", color: RED, text: MARK_REQUIRED_MISSING },
        { glyph: "✗", color: RED, text: MARK_ONE_OF_THESE_MISSING },
        { glyph: "✓", color: GREEN, text: MARK_REQUIRED_HERE },
        { glyph: "✓", color: GREEN, text: MARK_STARTS_THE_SYSTEM },
        { glyph: "✗", color: AMBER, text: MARK_MISSING_NEED_UNKNOWN },
        { glyph: "✗", color: AMBER, text: MARK_ONE_OF_THESE_UNSETTLED },
        { glyph: "✓", color: AMBER, text: MARK_HERE_NEED_UNKNOWN },
        { glyph: "?", color: AMBER, text: MARK_UNCHECKED },
        { glyph: "✓", color: PALE_GREEN, text: MARK_HERE },
        { glyph: "✗", color: MUTED, text: MARK_MISSING },
        { glyph: "✗", color: MUTED, text: MARK_ONE_OF_THESE_SPARE },
    ].filter((entry) => marks.some((mark) => mark.title === entry.text));
    if (files.some((file) => libraryMark(file) !== null)) {
        shown.push({ glyph: LIBRARY_MARK.glyph, color: LIBRARY_MARK.color, text: LIBRARY_MARK.title });
    }
    if (shown.length === 0)
        return null;
    return (SP_JSX.jsx("div", { "data-testid": "bios-legend", style: {
            display: "flex",
            flexDirection: "column",
            padding: "2px 16px 6px",
            fontSize: SECONDARY_FONT,
            lineHeight: 1.3,
        }, children: shown.map((entry) => (SP_JSX.jsxs("span", { style: { color: MUTED }, children: [SP_JSX.jsx("span", { style: { color: entry.color }, children: entry.glyph }), " ", entry.text] }, entry.text))) }));
};
const BiosFileRow = ({ file, systemImage, action, }) => {
    const { note, lines, fromLibrary } = biosFileNote(file);
    const mark = diskMark(file, systemImage);
    const library = libraryMark(file);
    const description = biosFileDescription(file);
    const folder = declaredFolder(file);
    const rowLines = fromLibrary ? [] : [...(note ? [note] : []), ...lines];
    return (SP_JSX.jsxs(PaneTableRow, { columns: TABLE_COLUMNS, focusStop: !action, cells: [
            {
                content: (SP_JSX.jsxs(SP_JSX.Fragment, { children: [folder && SP_JSX.jsx("span", { style: { color: MUTED }, children: folder }), file.file_name] })),
                title: file.declared_path ?? file.file_name,
            },
            {
                content: (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx("span", { "data-testid": "disk-mark", style: { color: mark.color }, title: mark.title, children: mark.glyph }), library && (SP_JSX.jsx("span", { "data-testid": "library-mark", style: { color: library.color }, title: library.title, children: library.glyph }))] })),
                style: { display: "flex", gap: "4px", fontSize: "14px", whiteSpace: "nowrap" },
                clip: false,
            },
            { content: contentsCell(file), style: { color: MUTED, fontSize: SECONDARY_FONT } },
            { content: action, clip: false },
        ], children: [description && (SP_JSX.jsx("div", { style: {
                    marginLeft: "18px",
                    fontSize: SECONDARY_FONT,
                    color: MUTED,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                }, children: description })), SP_JSX.jsx(BiosRowLines, { lines: rowLines })] }));
};
function coreOffer(row, core) {
    if (row.shortcutCount === 0) {
        return { kind: "blocked", reason: "Sync this platform first — the core applies to the games it puts in Steam." };
    }
    if (core === undefined)
        return { kind: "blocked", reason: "Reading the emulators for this platform…" };
    if (core === null) {
        const failed = "Could not read the emulators for this platform. Reopen the page to try again.";
        return { kind: "blocked", reason: failed, notice: failed };
    }
    if (!core.emulator_data_available) {
        const absent = "RetroDECK was not found, so there is no emulator list to choose from.";
        return { kind: "blocked", reason: absent, notice: absent };
    }
    if (core.emulators.length === 0) {
        const none = "RetroDECK lists no emulator for this platform, so its games will not launch.";
        return { kind: "blocked", reason: none, notice: none };
    }
    if (core.active_core_label === null) {
        const fallback = core.emulators[0];
        if (fallback?.reason === "not_installed") {
            return {
                kind: "blocked",
                reason: `RetroDECK would launch these with ${fallback.label}, which is not installed — and nothing here can pin a different one.`,
                notice: `RetroDECK would launch these with ${fallback.label}, which is not installed — and nothing here can pin a different one.`,
            };
        }
        return {
            kind: "blocked",
            reason: "None of this platform's emulators can be pinned from here, so RetroDECK picks one when a game launches.",
            notice: "None of this platform's emulators can be pinned from here, so RetroDECK picks one when a game launches.",
        };
    }
    if (core.emulators.length === 1) {
        return { kind: "blocked", reason: "This platform offers one emulator, so there is nothing to switch." };
    }
    return { kind: "pick", core };
}
const CoreNotice = ({ row, state, offer }) => (SP_JSX.jsxs(SP_JSX.Fragment, { children: [offer.kind === "blocked" && offer.notice !== undefined && SP_JSX.jsx(Muted, { children: offer.notice }), SP_JSX.jsx(GroupStatus, { status: scopedStatus(state.status), forKey: row.slug, scope: "core" })] }));
function downloadState(row, state, id) {
    if (state.busySlug !== row.slug)
        return null;
    if (state.downloadPending === id)
        return "spinner";
    return state.downloadFailed === id ? "failed" : null;
}
const FAILED_LABEL = SP_JSX.jsx("span", { style: { color: RED }, children: "Failed" });
function removeShortcutsTitle(row) {
    if (row.shortcutCount === null)
        return `Remove ${row.name} shortcuts?`;
    return `Remove ${row.shortcutCount} ${row.name} shortcut${row.shortcutCount === 1 ? "" : "s"}?`;
}
function coreClauseColour(unpinnable, isOverride) {
    if (unpinnable)
        return RED;
    return isOverride ? AMBER : MUTED;
}
function fallbackLabel(noEmulator, fallbackMissing) {
    if (noEmulator)
        return "no emulator";
    return fallbackMissing ? "no emulator installed" : "RetroDECK decides";
}
function downloadLabel(row, state, id, label, size) {
    const showing = downloadState(row, state, id);
    if (showing === "spinner")
        return SP_JSX.jsx(DFL.Spinner, { width: size, height: size });
    return showing === "failed" ? FAILED_LABEL : label;
}
function rowAction(row, state, file, fetchable) {
    const busy = state.busySlug !== null;
    if (fetchable.has(file.file_name) && !state.serverOffline) {
        return (SP_JSX.jsx(DFL.DialogButton, { style: ROW_BUTTON, disabled: busy, onClick: () => {
                state.downloadOne(row.slug, file.file_name);
            }, children: downloadLabel(row, state, file.file_name, "Download", 11) }));
    }
    const count = file.deletable_count ?? 0;
    if (count === 0)
        return null;
    const folder = file.declared_kind === "directory";
    const confirm = () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: folder ? `Delete ${count} file(s) in ${file.file_name}?` : `Delete ${file.file_name}?`, strDescription: "This deletes only what this plugin downloaded, at the places it wrote them. Files your emulator came with, or that you put there yourself, are never touched \u2014 and a folder the emulator lists is never removed. Games that need them won't launch until you download them again.", strOKButtonText: "Delete", strCancelButtonText: "Cancel", onOK: () => {
            if (folder)
                state.deleteBiosFolder(row.slug, file.local_path);
            else
                state.deleteBiosFile(row.slug, file.file_name);
        } }));
    return (SP_JSX.jsx(DFL.DialogButton, { style: ROW_BUTTON, disabled: busy, onClick: confirm, children: SP_JSX.jsx("span", { style: { color: RED }, children: folder ? `Delete (${count})` : "Delete" }) }));
}
const BiosSection = ({ row, state, firmware, }) => {
    const files = firmware.files;
    const total = firmware.server_count ?? files.filter((f) => f.on_server).length;
    const done = firmware.local_count ?? files.filter((f) => f.on_server && f.downloaded).length;
    const allDone = done === total;
    const requiredWithheld = firmware.required_withheld ?? 0;
    const systemImage = firmware.system_image ?? "not_demanded";
    const { status: summaryLabel, sentence: summaryDescription } = biosSummary(firmware, files, firmware.bios_level ?? null);
    const heldRatio = biosHeldRatio(firmware);
    const nothingEstablished = firmware.bios_level === "unknown" &&
        systemImage !== "absent" &&
        requiredWithheld === 0 &&
        systemImage !== "unsettled";
    const fetchableMissing = files.filter(isFetchable);
    const requiredMissing = fetchableMissing.filter((f) => f.required_by_active).length;
    const hasOptionalMissing = fetchableMissing.some((f) => !f.required_by_active);
    const showRequired = requiredMissing > 0 && !state.serverOffline;
    const showAll = !allDone && (hasOptionalMissing || requiredMissing > 0) && !state.serverOffline;
    const fetchable = new Set(fetchableMissing.map((f) => f.file_name));
    const deletable = firmware.deletable_count ?? 0;
    const unanswered = files.filter((f) => f.wanted === "unknown").length;
    const confirmDeleteBios = () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: `Delete BIOS files for ${row.name}?`, strDescription: "This deletes only the BIOS files this plugin downloaded for this system. Files your emulator came with, or that you put there yourself, are left where they are. Games that need the deleted files won't launch until you download them again.", strOKButtonText: "Delete BIOS Files", strCancelButtonText: "Cancel", onOK: () => state.deleteBios(row.slug) }));
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(SectionTitle, { title: "BIOS files", note: summaryLabel, noteColor: biosColorForLevel(firmware.bios_level ?? null) }), SP_JSX.jsx(Muted, { children: `${summaryDescription}${heldRatio}` }), nothingEstablished && SP_JSX.jsx(Muted, { children: "You can still put BIOS files in your BIOS folder by hand." }), files.length > 0 && SP_JSX.jsx(BiosTableHeader, {}), files.map((file) => (SP_JSX.jsx(BiosFileRow, { file: file, systemImage: systemImage, action: rowAction(row, state, file, fetchable) }, file.file_name))), files.length > 0 && SP_JSX.jsx(BiosLegend, { files: files, systemImage: systemImage }), unanswered > 0 && (SP_JSX.jsxs(Muted, { children: [unanswered === 1 ? "1 file" : `${unanswered} files`, " nothing installed could answer for. Report at github.com/danielcopper/romm-tender/issues if needed."] })), SP_JSX.jsxs(ButtonRow, { padding: "2px 16px 6px", children: [SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: !showRequired || state.busySlug !== null, onClick: () => state.downloadRequired(row.slug), children: downloadLabel(row, state, "required", `Download required (${requiredMissing})`, 12) }), SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: !showAll || state.busySlug !== null, onClick: () => state.downloadAll(row.slug), children: downloadLabel(row, state, "all", "Download all", 12) }), SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: deletable === 0 || state.busySlug !== null, onClick: confirmDeleteBios, children: SP_JSX.jsx("span", { style: { color: RED }, children: `Delete BIOS (${deletable})` }) })] }), SP_JSX.jsx(GroupStatus, { status: scopedStatus(state.status), forKey: row.slug, scope: "bios" })] }));
};
const RemoveSection = ({ row, state }) => {
    const syncRunning = useSyncRunning();
    const saveCount = state.saveCountFor(row.slug);
    const confirmDeleteSaves = () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: `Delete all save files for ${row.name}?`, strDescription: "This will delete every local save file for ROMs on this platform. Any local changes that haven't been uploaded to RomM yet will be lost permanently. Make sure saves are synced first.", strOKButtonText: "Delete Save Files", strCancelButtonText: "Cancel", onOK: () => state.deleteSaves(row) }));
    const confirmRemoveShortcuts = () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: removeShortcutsTitle(row), strDescription: "This takes this platform's games out of your Steam library. Downloaded ROM files and save files are left where they are, and the games come back on the next sync while the platform stays enabled.", strOKButtonText: "Remove Shortcuts", strCancelButtonText: "Cancel", onOK: () => state.removeShortcuts(row) }));
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs(ButtonRow, { padding: "6px 16px 4px", children: [SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: state.busySlug !== null || syncRunning || row.shortcutCount === 0, onClick: confirmRemoveShortcuts, children: SP_JSX.jsx("span", { style: { color: RED }, children: row.shortcutCount === null ? "Remove shortcuts" : `Remove ${pluralize(row.shortcutCount, "shortcut")}` }) }), SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: state.busySlug !== null || saveCount === undefined || saveCount === 0, onClick: confirmDeleteSaves, children: SP_JSX.jsxs("span", { style: { color: RED, display: "inline-flex", alignItems: "center", gap: "6px" }, children: [saveCount === undefined && SP_JSX.jsx(DFL.Spinner, { width: 12, height: 12 }), typeof saveCount === "number" ? `Delete ${pluralize(saveCount, "save file")}` : "Delete save files"] }) })] }), saveCount === null && (SP_JSX.jsx(Muted, { children: "Could not read how many save files this platform holds. Pick the platform again to retry." })), syncRunning && SP_JSX.jsx(Muted, { children: `Removing shortcuts: ${SYNC_RUNNING_HINT}` }), SP_JSX.jsx(GroupStatus, { status: scopedStatus(state.status), forKey: row.slug, scope: "remove" })] }));
};
const PlatformDetail = ({ row, state }) => {
    const core = state.coreFor(row.slug);
    const firmware = row.firmware;
    const offer = coreOffer(row, core);
    const activeLabel = core ? core.active_core_label : null;
    const emulatorsKnown = core != null && core.emulator_data_available;
    const noEmulator = emulatorsKnown && core.emulators.length === 0;
    const fallbackMissing = emulatorsKnown && activeLabel === null && core.emulators[0]?.reason === "not_installed";
    const activeIsDefault = core?.emulators.find((option) => option.label === activeLabel)?.is_default ?? false;
    const coreColor = coreClauseColour(noEmulator || fallbackMissing, activeLabel !== null && !activeIsDefault);
    const coreClause = !emulatorsKnown
        ? null
        : { text: activeLabel ?? fallbackLabel(noEmulator, fallbackMissing), color: coreColor };
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs(DFL.Focusable, { "flow-children": "horizontal", style: { display: "flex", alignItems: "baseline", gap: "10px", padding: "8px 16px 0" }, children: [SP_JSX.jsx("span", { style: { fontSize: "16px", fontWeight: 600, color: "#dcdedf", minWidth: 0 }, children: row.name }), SP_JSX.jsxs("span", { style: { flex: "1 1 auto", fontSize: SECONDARY_FONT, color: MUTED }, children: [`${row.romCount} on RomM`, row.reachableCount === null ? "" : ` · ${row.reachableCount} in Steam`, coreClause && SP_JSX.jsx("span", { style: { color: coreClause.color }, children: ` · ${coreClause.text}` })] }), SP_JSX.jsx(DFL.DialogButton, { style: CORE_BUTTON, title: offer.kind === "pick" ? "Emulator Core" : offer.reason, disabled: offer.kind !== "pick" || state.busySlug !== null, onClick: (e) => {
                            if (offer.kind !== "pick")
                                return;
                            DFL.showContextMenu(buildEmulatorMenu({
                                emulators: offer.core.emulators,
                                emulatorDataAvailable: offer.core.emulator_data_available,
                                activeLabel: offer.core.active_core_label,
                                platformCoreLabel: null,
                                onPick: (label) => state.changeCore(row.slug, label),
                            }), getEventTarget(e));
                        }, children: SP_JSX.jsx(FaMicrochip, { size: 16, color: coreColor }) })] }), state.shortcutCountsFailed && (SP_JSX.jsx(Muted, { children: "Could not read how many of these games are in Steam. Removing them still works, it just cannot say how many. Reopen the page to try again." })), state.removalProgress?.slug === row.slug && (SP_JSX.jsx(Muted, { children: `Removing ${state.removalProgress.removed} of ${state.removalProgress.total}…` })), SP_JSX.jsx(BusyElsewhere, { busyKey: state.busySlug, ownKey: row.slug, busyName: state.rows.get(state.busySlug ?? "")?.name ?? "another platform" }), SP_JSX.jsx(CoreNotice, { row: row, state: state, offer: offer }), SP_JSX.jsx(EmulatorInstallSection, { slug: row.slug }), row.firmwareStale && (SP_JSX.jsx(Muted, { children: "Could not re-read the BIOS state, so what is below may be out of date. Pick the platform again to retry." })), firmware ? (SP_JSX.jsx(BiosSection, { row: row, state: state, firmware: firmware })) : (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(SectionTitle, { title: "BIOS files" }), row.firmwareState === "pending" && SP_JSX.jsx(Muted, { children: "Checking what this platform needs\u2026" }), row.firmwareState === "failed" && (SP_JSX.jsx(Muted, { children: "Could not read the BIOS state. Pick the platform again to retry." })), row.firmwareState === "nothing" && SP_JSX.jsx(Muted, { children: "Nothing is known about this platform's BIOS files." })] })), SP_JSX.jsx(RemoveSection, { row: row, state: state })] }));
};

function biosTooltip(row) {
    if (row.firmwareState === "pending")
        return "Checking this platform's BIOS files…";
    if (row.firmwareState === "failed")
        return "Could not read this platform's BIOS state";
    const firmware = row.firmware;
    if (!firmware)
        return "Nothing is known about this platform's BIOS files";
    return biosSummary(firmware, firmware.files, firmware.bios_level ?? null).sentence;
}
const GroupHeading = ({ title, count }) => (SP_JSX.jsxs("div", { style: {
        padding: "8px 8px 2px",
        fontSize: "11px",
        fontWeight: 600,
        letterSpacing: "0.5px",
        color: "#8f98a0",
    }, children: [title.toUpperCase(), " (", count, ")"] }));
const RowLabel = ({ row, selected }) => {
    const level = row.firmware?.bios_level ?? null;
    const pending = row.firmwareState === "pending";
    return (SP_JSX.jsxs("span", { style: { display: "flex", alignItems: "center", gap: "6px", minWidth: 0 }, title: biosTooltip(row), children: [SP_JSX.jsx("span", { "data-testid": `bios-dot-${row.slug}`, style: {
                    display: "inline-block",
                    width: "8px",
                    height: "8px",
                    borderRadius: "50%",
                    boxSizing: "border-box",
                    backgroundColor: pending ? "transparent" : biosColorForLevel(level),
                    border: pending ? `1.5px solid ${biosColorForLevel(null)}` : undefined,
                    flexShrink: 0,
                } }), SP_JSX.jsx("span", { style: {
                    flex: "1 1 auto",
                    minWidth: 0,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                    fontWeight: selected ? 600 : 400,
                }, children: row.name })] }));
};
const PlatformsTab = ({ state }) => {
    if (state.loading)
        return SP_JSX.jsx(LoadingRow, {});
    if (state.failed) {
        return (SP_JSX.jsx("div", { style: { padding: "16px", color: "#8f98a0" }, children: "Could not read your platforms. Check the connection to RomM and open the page again." }));
    }
    const groups = state.groups;
    if (!groups || state.rows.size === 0) {
        return SP_JSX.jsx("div", { style: { padding: "16px", color: "#8f98a0" }, children: "RomM reports no platform holding any ROM." });
    }
    const items = [];
    const pushGroup = (slugs, title) => {
        slugs.forEach((slug, index) => {
            const row = state.rows.get(slug);
            if (!row)
                return;
            items.push({
                id: slug,
                render: (selected) => (SP_JSX.jsxs(SP_JSX.Fragment, { children: [index === 0 && SP_JSX.jsx(GroupHeading, { title: title, count: slugs.length }), SP_JSX.jsx("div", { style: {
                                borderLeft: `${ROW_MARKER_WIDTH}px solid ${selected ? SELECTION_ACCENT : "transparent"}`,
                                paddingLeft: `${ROW_MARKER_GAP}px`,
                            }, children: SP_JSX.jsx(DFL.ToggleField, { label: SP_JSX.jsx(RowLabel, { row: row, selected: selected }), checked: row.syncEnabled, bottomSeparator: "none", onChange: (value) => state.toggleSync(row, value) }) })] })),
            });
        });
    };
    pushGroup(groups.synced, "Synced");
    pushGroup(groups.available, "Available");
    const listHeader = (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs(DFL.Focusable, { "flow-children": "horizontal", style: { display: "flex", gap: "8px", padding: `4px 0 8px ${ROW_CONTENT_INSET}px` }, children: [SP_JSX.jsx(DFL.DialogButton, { style: { flex: 1, minWidth: 0, padding: "8px 0" }, onClick: () => state.setAllSync(true), children: "Enable all" }), SP_JSX.jsx(DFL.DialogButton, { style: { flex: 1, minWidth: 0, padding: "8px 0" }, onClick: () => state.setAllSync(false), children: "Disable all" })] }), state.listStatus && (SP_JSX.jsx("div", { "data-testid": "status-list", style: { fontSize: "12px", color: "#dcdedf", padding: `0 0 8px ${ROW_CONTENT_INSET}px` }, children: state.listStatus }))] }));
    return (SP_JSX.jsx(ListDetail, { items: items, listHeader: listHeader, selectedId: state.selectedSlug, onSelect: state.select, renderDetail: (slug) => {
            const row = slug === null ? undefined : state.rows.get(slug);
            if (!row)
                return SP_JSX.jsx("div", { style: { padding: "16px", color: "#8f98a0" }, children: "Pick a platform on the left." });
            return SP_JSX.jsx(PlatformDetail, { row: row, state: state });
        } }));
};

const REMOVAL_CHUNK_SIZE = 25;
const REMOVAL_CHUNK_DELAY_MS = 50;
async function removeShortcutsPaced(appIds, onProgress, signal) {
    const total = appIds.length;
    await pacedForEach(appIds, (appId) => removeShortcut(appId), {
        chunkSize: REMOVAL_CHUNK_SIZE,
        delayMs: REMOVAL_CHUNK_DELAY_MS,
        ...(onProgress ? { onProgress: (completed) => onProgress(completed, total) } : {}),
        ...(signal ? { isCancelled: () => signal.aborted } : {}),
    });
}

const FAILED_NOTICE_MS = 2000;
const LEASE_OWNER = "library-platforms";
const REMOVAL_REPORT_TIMEOUT_MS$1 = 15000;
const SYNC_WRITE_FAILED = "Could not save that; the change was undone.";
function announceBiosChange(platformSlug) {
    globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "bios", platform_slug: platformSlug } }));
}
function freezeGroups(platforms) {
    const byName = [...platforms].sort((a, b) => a.name.localeCompare(b.name));
    return {
        synced: byName.filter((p) => p.sync_enabled).map((p) => p.slug),
        available: byName.filter((p) => !p.sync_enabled).map((p) => p.slug),
    };
}
function usePlatformsPage() {
    const [platforms, setPlatforms] = SP_REACT.useState([]);
    const [groups, setGroups] = SP_REACT.useState(null);
    const [loading, setLoading] = SP_REACT.useState(true);
    const [failed, setFailed] = SP_REACT.useState(false);
    const [named, setNamed] = SP_REACT.useState(null);
    const [firmware, setFirmware] = SP_REACT.useState({});
    const [readFailed, setReadFailed] = SP_REACT.useState({});
    const [serverOffline, setServerOffline] = SP_REACT.useState(false);
    const [overviewFailed, setOverviewFailed] = SP_REACT.useState(false);
    const [downloadPending, setDownloadPending] = SP_REACT.useState(null);
    const [downloadFailed, setDownloadFailed] = SP_REACT.useState(null);
    const failedTimer = SP_REACT.useRef(null);
    SP_REACT.useEffect(() => () => {
        if (failedTimer.current !== null)
            clearTimeout(failedTimer.current);
    }, []);
    const [shortcutCounts, setShortcutCounts] = SP_REACT.useState({});
    const [shortcutCountsFailed, setShortcutCountsFailed] = SP_REACT.useState(false);
    const [selectedSlug, setSelectedSlug] = SP_REACT.useState(null);
    const [cores, setCores] = SP_REACT.useState({});
    const [saveCounts, setSaveCounts] = SP_REACT.useState({});
    const [status, setStatus] = SP_REACT.useState(null);
    const [listStatus, setListStatus] = SP_REACT.useState(null);
    const [busySlug, setBusySlug] = SP_REACT.useState(null);
    const [removalProgress, setRemovalProgress] = SP_REACT.useState(null);
    const coreRequested = SP_REACT.useRef(new Set());
    const saveCountRequested = SP_REACT.useRef(new Set());
    const alive = SP_REACT.useRef(true);
    SP_REACT.useEffect(() => {
        alive.current = true;
        return () => {
            alive.current = false;
        };
    }, []);
    const readSeq = SP_REACT.useRef(new Map());
    const asked = SP_REACT.useRef(new Set());
    const accept = SP_REACT.useCallback((slug, seq) => alive.current && readSeq.current.get(slug) === seq, []);
    const readPlatform = SP_REACT.useCallback(async (slug) => {
        asked.current.add(slug);
        const seq = (readSeq.current.get(slug) ?? 0) + 1;
        readSeq.current.set(slug, seq);
        try {
            const result = await getPlatformFirmwareStatus(slug);
            if (!accept(slug, seq))
                return;
            if (!result.success) {
                logWarn(`BIOS state for ${slug} answered a failure: ${result.message ?? "no message"}`);
                setReadFailed((prev) => ({ ...prev, [slug]: true }));
                return;
            }
            setFirmware((prev) => ({ ...prev, [slug]: result.platform }));
            setReadFailed((prev) => {
                if (!(slug in prev))
                    return prev;
                const next = { ...prev };
                delete next[slug];
                return next;
            });
        }
        catch (e) {
            logWarn(`Failed to read the BIOS state for ${slug}: ${e}`);
            if (!accept(slug, seq))
                return;
            setReadFailed((prev) => ({ ...prev, [slug]: true }));
        }
    }, [accept]);
    const readOverview = SP_REACT.useCallback(async () => {
        try {
            const result = await getFirmwareStatus();
            if (!alive.current)
                return;
            if (!result.success) {
                logWarn(`Firmware overview answered a failure: ${result.message ?? "no message"}`);
                setOverviewFailed(true);
                return;
            }
            setServerOffline(result.server_offline ?? false);
            setNamed(new Set(result.platforms.map((p) => p.platform_slug)));
            setOverviewFailed(false);
        }
        catch (e) {
            logWarn(`Failed to read the firmware overview: ${e}`);
            if (!alive.current)
                return;
            setOverviewFailed(true);
        }
    }, []);
    const refreshShortcutCounts = SP_REACT.useCallback(async () => {
        try {
            const result = await getRegistryPlatforms();
            setShortcutCounts(Object.fromEntries(result.platforms.map((p) => [p.slug, { bound: p.count, reachable: p.reachable_count ?? p.count }])));
            setShortcutCountsFailed(false);
        }
        catch (e) {
            logWarn(`Failed to read platform shortcut counts: ${e}`);
            setShortcutCountsFailed(true);
        }
    }, []);
    const selectedRef = SP_REACT.useRef(null);
    SP_REACT.useEffect(() => {
        selectedRef.current = selectedSlug;
    }, [selectedSlug]);
    SP_REACT.useEffect(() => {
        if (named === null || groups === null)
            return;
        const order = [...groups.synced, ...groups.available].filter((slug) => named.has(slug));
        let walking = true;
        const next = () => {
            const focused = selectedRef.current;
            if (focused !== null && named.has(focused) && !asked.current.has(focused))
                return focused;
            return order.find((slug) => !asked.current.has(slug)) ?? null;
        };
        const walk = async () => {
            for (let slug = next(); slug !== null && walking && alive.current; slug = next()) {
                await readPlatform(slug);
            }
        };
        detach(walk());
        return () => {
            walking = false;
        };
    }, [groups, named, readPlatform]);
    const loadCore = SP_REACT.useCallback((slug) => {
        if (coreRequested.current.has(slug))
            return;
        coreRequested.current.add(slug);
        getSystemCoreInfo(slug)
            .then((info) => setCores((prev) => ({ ...prev, [slug]: info })))
            .catch((e) => {
            logWarn(`Failed to read the core for ${slug}: ${e}`);
            setCores((prev) => ({ ...prev, [slug]: null }));
        });
    }, []);
    const loadSaveCount = SP_REACT.useCallback((slug) => {
        if (saveCountRequested.current.has(slug))
            return;
        saveCountRequested.current.add(slug);
        setSaveCounts((prev) => {
            if (!(slug in prev))
                return prev;
            const next = { ...prev };
            delete next[slug];
            return next;
        });
        countPlatformSaves(slug)
            .then((result) => setSaveCounts((prev) => ({ ...prev, [slug]: result.count })))
            .catch((e) => {
            logWarn(`Failed to count the save files for ${slug}: ${e}`);
            saveCountRequested.current.delete(slug);
            setSaveCounts((prev) => ({ ...prev, [slug]: null }));
        });
    }, []);
    const reloadSaveCount = SP_REACT.useCallback((slug) => {
        saveCountRequested.current.delete(slug);
        loadSaveCount(slug);
    }, [loadSaveCount]);
    const reloadCore = SP_REACT.useCallback((slug) => {
        coreRequested.current.delete(slug);
        setCores((prev) => {
            const next = { ...prev };
            delete next[slug];
            return next;
        });
        loadCore(slug);
    }, [loadCore]);
    SP_REACT.useEffect(() => {
        mountPruneLeaseOwner(LEASE_OWNER);
        getPlatforms()
            .then((result) => {
            if (!result.success) {
                setFailed(true);
                return;
            }
            setPlatforms(result.platforms);
            const frozen = freezeGroups(result.platforms);
            setGroups(frozen);
            const first = frozen.synced[0] ?? frozen.available[0] ?? null;
            setSelectedSlug(first);
            if (first) {
                loadCore(first);
                loadSaveCount(first);
            }
        })
            .catch(() => setFailed(true))
            .finally(() => setLoading(false));
        detach(readOverview());
        detach(refreshShortcutCounts());
        return () => {
            detach(releasePruneLeasesByOwner(LEASE_OWNER));
        };
    }, [loadCore, loadSaveCount, readOverview, refreshShortcutCounts]);
    const firmwareStateFor = (slug) => {
        if (slug in firmware)
            return firmware[slug] !== null ? "answered" : "nothing";
        if (named !== null && !named.has(slug))
            return "nothing";
        if (readFailed[slug] || overviewFailed)
            return "failed";
        return "pending";
    };
    const firmwareHeldFor = (slug) => slug in firmware || (named !== null && !named.has(slug));
    const rows = new Map(platforms.map((p) => [
        p.slug,
        {
            id: p.id,
            slug: p.slug,
            name: p.name,
            romCount: p.rom_count,
            syncEnabled: p.sync_enabled,
            firmware: firmware[p.slug] ?? null,
            firmwareState: firmwareStateFor(p.slug),
            firmwareStale: readFailed[p.slug] === true && firmwareHeldFor(p.slug),
            shortcutCount: shortcutCountsFailed ? null : (shortcutCounts[p.slug]?.bound ?? 0),
            reachableCount: shortcutCountsFailed ? null : (shortcutCounts[p.slug]?.reachable ?? 0),
        },
    ]));
    const select = SP_REACT.useCallback((slug) => {
        setSelectedSlug(slug);
        loadCore(slug);
        loadSaveCount(slug);
        if (readFailed[slug])
            detach(readPlatform(slug));
        else if (overviewFailed)
            detach(readOverview());
    }, [loadCore, loadSaveCount, overviewFailed, readFailed, readOverview, readPlatform]);
    const coreFor = SP_REACT.useCallback((slug) => cores[slug], [cores]);
    const saveCountFor = SP_REACT.useCallback((slug) => saveCounts[slug], [saveCounts]);
    const platformsRef = SP_REACT.useRef([]);
    SP_REACT.useEffect(() => {
        platformsRef.current = platforms;
    }, [platforms]);
    const toggleSync = SP_REACT.useCallback((row, enabled) => {
        const flip = (want) => setPlatforms((prev) => prev.map((p) => (p.slug === row.slug ? { ...p, sync_enabled: want } : p)));
        flip(enabled);
        detach(savePlatformSync(row.id, enabled)
            .then((result) => {
            if (result.success) {
                setListStatus(null);
                return;
            }
            flip(!enabled);
            setListStatus(result.message || SYNC_WRITE_FAILED);
        })
            .catch(() => {
            flip(!enabled);
            setListStatus(SYNC_WRITE_FAILED);
        }));
    }, []);
    const setAllSync = SP_REACT.useCallback((enabled) => {
        const previous = platformsRef.current;
        setPlatforms((prev) => prev.map((p) => ({ ...p, sync_enabled: enabled })));
        detach(setAllPlatformsSync(enabled)
            .then((result) => {
            if (result.success) {
                setListStatus(null);
                return;
            }
            setPlatforms(previous);
            setListStatus(result.message || SYNC_WRITE_FAILED);
        })
            .catch(() => {
            setPlatforms(previous);
            setListStatus(SYNC_WRITE_FAILED);
        }));
    }, []);
    const clearCoreLine = SP_REACT.useCallback((slug) => {
        setStatus((prev) => (prev?.slug === slug && prev.scope === "core" ? null : prev));
    }, []);
    const changeCore = SP_REACT.useCallback((slug, pickedLabel) => {
        const answer = cores[slug];
        const defaultLabel = answer?.emulators.find((e) => e.is_default)?.label;
        const label = pickedLabel === defaultLabel ? "" : pickedLabel;
        setBusySlug(slug);
        setStatus({ slug, scope: "core", text: `Switching to ${pickedLabel}…` });
        const admission = capturePruneLeaseAdmission(LEASE_OWNER);
        detach(debugLog(`setSystemCore: slug=${slug} label=${label} (selected=${pickedLabel})`));
        detach((async () => {
            try {
                const result = await setSystemCore(slug, label);
                detach(debugLog(`setSystemCore: result success=${result.success}`));
                if (!result.success) {
                    setStatus({ slug, scope: "core", text: result.message ?? "Could not change the core" });
                    return;
                }
                await withPruneLease(result.prune_lease_token, "setSystemCore", (signal) => batchConfirmLaunchOptions(result.rebake_items ?? [], "setSystemCore", signal), LEASE_OWNER, admission);
                clearCoreLine(slug);
                reloadCore(slug);
                await readPlatform(slug);
                globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "core_changed", platform_slug: slug } }));
            }
            catch (e) {
                if (isPruneLeaseCancellation(e, admission)) {
                    logWarn(`Core switch continuation was cancelled: ${e}`);
                    clearCoreLine(slug);
                    return;
                }
                detach(debugLog(`setSystemCore: error: ${e}`));
                setStatus({ slug, scope: "core", text: "Could not change the core" });
            }
            finally {
                setBusySlug(null);
            }
        })());
    }, [clearCoreLine, cores, readPlatform, reloadCore]);
    const reportFailure = SP_REACT.useCallback((pending) => {
        setDownloadPending(null);
        setDownloadFailed(pending);
        failedTimer.current = setTimeout(() => {
            failedTimer.current = null;
            setDownloadFailed(null);
            setBusySlug(null);
        }, FAILED_NOTICE_MS);
    }, []);
    const runDownload = SP_REACT.useCallback((slug, pending, work) => {
        setBusySlug(slug);
        setDownloadPending(pending);
        setStatus(null);
        detach((async () => {
            try {
                const result = await work();
                if (result.success) {
                    await readPlatform(slug);
                    if ((result.downloaded ?? 0) > 0)
                        announceBiosChange(slug);
                    setDownloadPending(null);
                    setBusySlug(null);
                    return;
                }
                setStatus({ slug, scope: "bios", text: result.message ?? "Download failed" });
                reportFailure(pending);
            }
            catch (e) {
                setStatus({ slug, scope: "bios", text: `Download failed: ${e}` });
                reportFailure(pending);
            }
        })());
    }, [readPlatform, reportFailure]);
    const downloadRequired = SP_REACT.useCallback((slug) => runDownload(slug, "required", () => downloadRequiredFirmware(slug)), [runDownload]);
    const downloadAll = SP_REACT.useCallback((slug) => runDownload(slug, "all", () => downloadAllFirmware(slug)), [runDownload]);
    const downloadOne = SP_REACT.useCallback((slug, fileName) => runDownload(slug, fileName, () => downloadPlatformFirmwareFile(slug, fileName)), [runDownload]);
    const deleteBios = SP_REACT.useCallback((slug) => {
        setBusySlug(slug);
        detach((async () => {
            try {
                const result = await deletePlatformBios(slug);
                setStatus({ slug, scope: "bios", text: result.message });
                if (result.success) {
                    await readPlatform(slug);
                    if (result.deleted_count > 0)
                        announceBiosChange(slug);
                }
            }
            catch (e) {
                setStatus({ slug, scope: "bios", text: `Failed to delete BIOS files: ${e}` });
            }
            finally {
                setBusySlug(null);
            }
        })());
    }, [readPlatform]);
    const runRowDelete = SP_REACT.useCallback((slug, work, what) => {
        setBusySlug(slug);
        setStatus(null);
        detach((async () => {
            try {
                const result = await work();
                if (result.success) {
                    await readPlatform(slug);
                    if (result.deleted_count > 0)
                        announceBiosChange(slug);
                }
                else {
                    setStatus({ slug, scope: "bios", text: result.message });
                }
            }
            catch (e) {
                setStatus({ slug, scope: "bios", text: `Failed to delete ${what}: ${e}` });
            }
            finally {
                setBusySlug(null);
            }
        })());
    }, [readPlatform]);
    const deleteBiosFile$1 = SP_REACT.useCallback((slug, fileName) => {
        runRowDelete(slug, () => deleteBiosFile(slug, fileName), fileName);
    }, [runRowDelete]);
    const deleteBiosFolder$1 = SP_REACT.useCallback((slug, folderPath) => {
        runRowDelete(slug, () => deleteBiosFolder(slug, folderPath), "these files");
    }, [runRowDelete]);
    const removeShortcuts = SP_REACT.useCallback((row) => {
        setBusySlug(row.slug);
        setStatus({ slug: row.slug, scope: "remove", text: `Removing ${row.name} shortcuts…` });
        const admission = capturePruneLeaseAdmission(LEASE_OWNER);
        detach((async () => {
            try {
                const result = await removePlatformShortcuts(row.slug);
                if (!result.success) {
                    setStatus({ slug: row.slug, scope: "remove", text: result.message ?? "Failed to remove shortcuts" });
                    return;
                }
                await withPruneLease(result.prune_lease_token, "Platform shortcut removal", async (signal) => {
                    await removeShortcutsPaced(result.app_ids ?? [], (removed, total) => setRemovalProgress({ slug: row.slug, removed, total }), signal);
                    if (isPruneLeaseCancelled(signal))
                        return;
                    await clearPlatformCollection(result.platform_name || row.name, signal);
                    if (isPruneLeaseCancelled(signal))
                        return;
                    if (result.rom_ids?.length || result.prune_lease_token) {
                        await withTimeout(reportRemovalResults(result.rom_ids ?? [], result.prune_lease_token ?? null), REMOVAL_REPORT_TIMEOUT_MS$1);
                    }
                }, LEASE_OWNER, admission);
                const removed = result.app_ids?.length ?? 0;
                setStatus({
                    slug: row.slug,
                    scope: "remove",
                    text: `Removed ${removed} ${row.name} game${removed === 1 ? "" : "s"}`,
                });
                await refreshShortcutCounts();
            }
            catch (e) {
                if (isPruneLeaseCancellation(e, admission)) {
                    logWarn(`Platform shortcut removal continuation was cancelled: ${e}`);
                    return;
                }
                setStatus({ slug: row.slug, scope: "remove", text: "Failed to remove shortcuts" });
            }
            finally {
                setBusySlug(null);
                setRemovalProgress(null);
            }
        })());
    }, [refreshShortcutCounts]);
    const deleteSaves = SP_REACT.useCallback((row) => {
        setBusySlug(row.slug);
        setStatus({ slug: row.slug, scope: "remove", text: `Deleting ${row.name} saves…` });
        detach((async () => {
            try {
                const result = await deletePlatformSaves(row.slug);
                setStatus({ slug: row.slug, scope: "remove", text: result.message });
                globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "save_sync" } }));
            }
            catch {
                setStatus({ slug: row.slug, scope: "remove", text: "Failed to delete saves" });
            }
            finally {
                setBusySlug(null);
                reloadSaveCount(row.slug);
            }
        })());
    }, [reloadSaveCount]);
    return {
        rows,
        groups,
        loading,
        failed,
        serverOffline,
        shortcutCountsFailed,
        selectedSlug,
        select,
        coreFor,
        saveCountFor,
        status,
        listStatus,
        busySlug,
        removalProgress,
        toggleSync,
        setAllSync,
        changeCore,
        downloadPending,
        downloadFailed,
        downloadRequired,
        downloadAll,
        downloadOne,
        deleteBios,
        deleteBiosFile: deleteBiosFile$1,
        deleteBiosFolder: deleteBiosFolder$1,
        removeShortcuts,
        deleteSaves,
    };
}

const SUB_TAB_ORDER = ["standard", "smart", "virtual"];
const SUB_TAB_LABELS = {
    standard: "Standard",
    smart: "Smart",
    virtual: "Virtual",
};
const SUB_TAB_HEADERS = {
    standard: "STANDARD COLLECTIONS",
    smart: "SMART COLLECTIONS",
    virtual: "VIRTUAL",
};
const COLLECTION_RENDER_CAP = 50;
const VIRTUAL_TYPE_FILTER_ORDER = ["all", "franchise", "collection"];
const VIRTUAL_TYPE_LABELS = {
    franchise: "Franchise",
    collection: "IGDB Collection",
};
const VIRTUAL_TYPE_FILTER_LABELS = {
    all: "All",
    franchise: VIRTUAL_TYPE_LABELS.franchise,
    collection: VIRTUAL_TYPE_LABELS.collection,
};
function collectionRowDescription(c) {
    if (c.kind === "virtual" && c.virtual_type) {
        return `${VIRTUAL_TYPE_LABELS[c.virtual_type]} · ${c.rom_count} ROMs`;
    }
    return `${c.rom_count} ROMs`;
}
function filterCollectionsBySubTab(collections, subTab, includeFavoritesInMy = false) {
    switch (subTab) {
        case "standard":
            return collections.filter((c) => c.kind === "standard" && (includeFavoritesInMy || !c.is_favorite));
        case "smart":
            return collections.filter((c) => c.kind === "smart");
        case "virtual":
            return collections.filter((c) => c.kind === "virtual");
    }
}
function filterCollectionsByOwnerScope(collections, ownerScope) {
    if (ownerScope === "all")
        return collections;
    return collections.filter((c) => c.is_own !== false);
}
function favoritesDescription(romCount) {
    if (romCount === 1)
        return "Includes 1 favorited ROM";
    return `Includes ${romCount} favorited ROMs`;
}
const LibraryPage = ({ onBack }) => {
    const [activeTab, setActiveTab] = SP_REACT.useState("platforms");
    const platformsState = usePlatformsPage();
    const [collections, setCollections] = SP_REACT.useState([]);
    const [collectionsLoading, setCollectionsLoading] = SP_REACT.useState(true);
    const [collectionsError, setCollectionsError] = SP_REACT.useState(false);
    const collectionsLoaded = SP_REACT.useRef(false);
    const [ownerScope, setOwnerScope] = SP_REACT.useState("all");
    const [activeSubTab, setActiveSubTab] = SP_REACT.useState("standard");
    const [search, setSearch] = SP_REACT.useState("");
    const [virtualTypeFilter, setVirtualTypeFilter] = SP_REACT.useState("all");
    const [collectionsStatus, setCollectionsStatus] = SP_REACT.useState(null);
    const searchFieldRef = SP_REACT.useRef(null);
    const scrollSearchToTop = () => {
        scrollElementToTop(searchFieldRef.current);
    };
    const favoritesCollection = SP_REACT.useMemo(() => {
        const favs = collections.filter((c) => c.kind === "standard" && c.is_favorite);
        if (favs.length === 0)
            return null;
        if (favs.length > 1) {
            console.warn(`romm-tender: expected at most one favorites collection, got ${favs.length}. ` +
                `Falling back to listing them in the Standard sub-tab.`);
            return null;
        }
        return favs[0] ?? null;
    }, [collections]);
    SP_REACT.useEffect(() => {
        if (activeTab === "collections" && !collectionsLoaded.current) {
            collectionsLoaded.current = true;
            getSettings()
                .then((settingsResult) => {
                setOwnerScope(settingsResult.collection_owner_scope === "own" ? "own" : "all");
            })
                .catch(() => {
            });
            getCollections()
                .then((collResult) => {
                if (collResult.success) {
                    setCollections(collResult.collections);
                }
                else {
                    setCollectionsError(true);
                }
            })
                .catch(() => setCollectionsError(true))
                .finally(() => setCollectionsLoading(false));
        }
    }, [activeTab]);
    const handleCollectionsTabClick = () => {
        setActiveSubTab("standard");
        setSearch("");
        setVirtualTypeFilter("all");
        setCollectionsStatus(null);
        setActiveTab("collections");
    };
    const handleSubTabChange = (sub) => {
        setActiveSubTab(sub);
        setSearch("");
        setVirtualTypeFilter("all");
        setCollectionsStatus(null);
    };
    const handleCollectionToggle = async (id, kind, enabled) => {
        const revert = () => setCollections((prev) => prev.map((c) => (c.id === id && c.kind === kind ? { ...c, sync_enabled: !enabled } : c)));
        setCollections((prev) => prev.map((c) => (c.id === id && c.kind === kind ? { ...c, sync_enabled: enabled } : c)));
        try {
            const result = await saveCollectionSync(id, kind, enabled);
            if (!result.success) {
                revert();
                setCollectionsStatus(result.message || SYNC_WRITE_FAILED);
                return;
            }
            setCollectionsStatus(null);
        }
        catch {
            revert();
            setCollectionsStatus(SYNC_WRITE_FAILED);
        }
    };
    const handleSetAllCollections = async (enabled, scope) => {
        const previous = collections.map((c) => ({ ...c }));
        setCollections((prev) => prev.map((c) => (filterCollectionsBySubTab([c], scope).length > 0 ? { ...c, sync_enabled: enabled } : c)));
        try {
            const result = await setAllCollectionsSync(enabled, scope);
            if (!result.success) {
                setCollections(previous);
                setCollectionsStatus(result.message || SYNC_WRITE_FAILED);
                return;
            }
            setCollectionsStatus(null);
        }
        catch {
            setCollections(previous);
            setCollectionsStatus(SYNC_WRITE_FAILED);
        }
    };
    const handleBatchCollectionsSync = async (enabled, kind, ids) => {
        if (ids.length === 0)
            return;
        const idSet = new Set(ids);
        const previous = collections.map((c) => ({ ...c }));
        setCollections((prev) => prev.map((c) => (c.kind === kind && idSet.has(c.id) ? { ...c, sync_enabled: enabled } : c)));
        try {
            const result = await saveCollectionsSync(ids, kind, enabled);
            if (!result.success) {
                setCollections(previous);
                setCollectionsStatus(result.message || SYNC_WRITE_FAILED);
                return;
            }
            setCollectionsStatus(null);
        }
        catch {
            setCollections(previous);
            setCollectionsStatus(SYNC_WRITE_FAILED);
        }
    };
    const handleCollectionsSetAll = (enabled, isWholeKind, matchedIds) => {
        const kind = activeSubTab;
        if (isWholeKind) {
            const label = SUB_TAB_LABELS[activeSubTab];
            DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: enabled ? `Enable all ${label} collections?` : `Disable all ${label} collections?`, strDescription: enabled
                    ? `This turns on syncing for every collection in the ${label} tab, including any not currently shown. On a large library this can be a lot of collections.`
                    : `This turns off syncing for every collection in the ${label} tab, including any not currently shown.`, strOKButtonText: enabled ? "Enable All" : "Disable All", strCancelButtonText: "Cancel", onOK: () => {
                    detach(handleSetAllCollections(enabled, activeSubTab));
                } }));
            return;
        }
        detach(handleBatchCollectionsSync(enabled, kind, matchedIds));
    };
    const handleOwnerScopeChange = async (scope) => {
        if (scope === ownerScope)
            return;
        const previous = ownerScope;
        setOwnerScope(scope);
        try {
            const result = await setCollectionOwnerScope(scope);
            if (!result.success) {
                setOwnerScope(previous);
                setCollectionsStatus(result.message || SYNC_WRITE_FAILED);
                return;
            }
            setCollectionsStatus(null);
        }
        catch {
            setOwnerScope(previous);
            setCollectionsStatus(SYNC_WRITE_FAILED);
        }
    };
    const renderCollectionsContent = () => {
        const hasCollections = collections.length > 0;
        const includeFavoritesInMy = favoritesCollection === null;
        const kindFiltered = filterCollectionsBySubTab(collections, activeSubTab, includeFavoritesInMy);
        const scopeFiltered = filterCollectionsByOwnerScope(kindFiltered, ownerScope);
        const showTypeFilter = activeSubTab === "virtual";
        const typeFiltered = showTypeFilter && virtualTypeFilter !== "all"
            ? scopeFiltered.filter((c) => c.virtual_type === virtualTypeFilter)
            : scopeFiltered;
        const matched = search ? typeFiltered.filter((c) => fuzzyMatch(search, c.name)) : typeFiltered;
        const rendered = matched.slice(0, COLLECTION_RENDER_CAP);
        const overflow = matched.length - rendered.length;
        const isWholeKind = search === "" && ownerScope === "all" && !(showTypeFilter && virtualTypeFilter !== "all");
        const matchedIds = matched.map((c) => c.id);
        const activeLabel = SUB_TAB_LABELS[activeSubTab];
        const sectionTitle = hasCollections
            ? `${SUB_TAB_HEADERS[activeSubTab]} (${matched.length})`
            : SUB_TAB_HEADERS[activeSubTab];
        return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSection, { children: SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: "Sync RomM favorites", description: favoritesCollection ? favoritesDescription(favoritesCollection.rom_count) : undefined, checked: favoritesCollection ? favoritesCollection.sync_enabled : false, disabled: favoritesCollection === null, onChange: (value) => {
                                if (!favoritesCollection)
                                    return;
                                detach(handleCollectionToggle(favoritesCollection.id, favoritesCollection.kind, value));
                            } }) }) }), SP_JSX.jsxs(DFL.PanelSection, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { style: { marginTop: "-8px" }, children: SP_JSX.jsx(DFL.Field, { label: "Show collections", description: ownerScope === "own"
                                        ? "Only your own collections (virtual collections have no owner, so they always appear)."
                                        : "Every collection on the server, including other users' public ones." }) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Focusable, { "flow-children": "horizontal", style: { display: "flex", gap: "8px" }, children: ["all", "own"].map((scope) => (SP_JSX.jsx(DFL.DialogButton, { style: {
                                        flex: 1,
                                        minWidth: 0,
                                        padding: "8px 0",
                                        opacity: ownerScope === scope ? 1 : 0.5,
                                        borderBottom: ownerScope === scope ? "2px solid #1a9fff" : "2px solid transparent",
                                    }, onClick: () => {
                                        detach(handleOwnerScopeChange(scope));
                                    }, children: scope === "own" ? "Mine" : "All" }, scope))) }) })] }), SP_JSX.jsx(DFL.Focusable, { "flow-children": "horizontal", style: { display: "flex", gap: "8px", padding: "0 16px 12px" }, children: SUB_TAB_ORDER.map((sub) => (SP_JSX.jsx(DFL.DialogButton, { style: {
                            flex: 1,
                            minWidth: 0,
                            padding: "8px 0",
                            opacity: activeSubTab === sub ? 1 : 0.5,
                            borderBottom: activeSubTab === sub ? "2px solid #1a9fff" : "2px solid transparent",
                        }, onClick: () => handleSubTabChange(sub), children: SUB_TAB_LABELS[sub] }, sub))) }), SP_JSX.jsxs(DFL.PanelSection, { title: sectionTitle, children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { ref: searchFieldRef, children: SP_JSX.jsx(DFL.TextField, { label: "Search collections (fuzzy)", value: search, onChange: (e) => {
                                        const value = e.target.value;
                                        if (search === "" && value !== "") {
                                            scrollSearchToTop();
                                        }
                                        setSearch(value);
                                    }, onFocus: scrollSearchToTop }) }) }), showTypeFilter && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Focusable, { "flow-children": "horizontal", style: { display: "flex", gap: "8px", alignItems: "stretch", marginBottom: "12px" }, children: VIRTUAL_TYPE_FILTER_ORDER.map((type) => (SP_JSX.jsx(DFL.DialogButton, { style: {
                                        flex: 1,
                                        minWidth: 0,
                                        padding: "8px 4px",
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        textAlign: "center",
                                        opacity: virtualTypeFilter === type ? 1 : 0.5,
                                        borderBottom: virtualTypeFilter === type ? "2px solid #1a9fff" : "2px solid transparent",
                                    }, onClick: () => setVirtualTypeFilter(type), children: VIRTUAL_TYPE_FILTER_LABELS[type] }, type))) }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs(DFL.Focusable, { "flow-children": "horizontal", style: { display: "flex", gap: "8px" }, children: [SP_JSX.jsx(DFL.DialogButton, { style: { flex: 1, minWidth: 0 }, disabled: !hasCollections, onClick: () => handleCollectionsSetAll(true, isWholeKind, matchedIds), children: "Enable All" }), SP_JSX.jsx(DFL.DialogButton, { style: { flex: 1, minWidth: 0 }, disabled: !hasCollections, onClick: () => handleCollectionsSetAll(false, isWholeKind, matchedIds), children: "Disable All" })] }) }), collectionsStatus && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx("div", { "data-testid": "collections-status", style: { fontSize: "12px", color: "#dcdedf" }, children: collectionsStatus }) })), renderCollectionListBody(matched, rendered, overflow, activeLabel)] })] }));
    };
    const renderCollectionListBody = (matched, rendered, overflow, activeLabel) => {
        if (collectionsLoading) {
            return SP_JSX.jsx(LoadingRow, {});
        }
        if (collectionsError) {
            return (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "Failed to load collections", description: "Check your connection and try again" }) }));
        }
        if (collections.length === 0) {
            return (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "No collections found", description: "Create collections in RomM to sync them here" }) }));
        }
        if (matched.length === 0) {
            return (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: search
                        ? `No ${activeLabel.toLowerCase()} collections match your search`
                        : `No ${activeLabel.toLowerCase()} collections` }) }));
        }
        return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [rendered.map((collection) => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: collection.name, description: collectionRowDescription(collection), checked: collection.sync_enabled, onChange: (value) => {
                            detach(handleCollectionToggle(collection.id, collection.kind, value));
                        } }) }, `${collection.kind}:${collection.id}`))), overflow > 0 && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: `${overflow} more — refine your search`, description: "Type in the search box above to narrow the list." }) }))] }));
    };
    const tabs = [
        { id: "platforms", title: "Platforms", content: SP_JSX.jsx(PlatformsTab, { state: platformsState }) },
        { id: "collections", title: "Collections", content: SP_JSX.jsx(SP_JSX.Fragment, { children: renderCollectionsContent() }) },
    ];
    return (SP_JSX.jsx(WidePage, { title: "Library", onBack: onBack, tabs: tabs, activeTab: activeTab, onShowTab: (tabId) => {
            if (tabId === "collections") {
                handleCollectionsTabClick();
                return;
            }
            setActiveTab("platforms");
        } }));
};

const HIGH_HEAP_KB = 1800000;
function formatGb(kb) {
    return `${(kb / 1000000).toFixed(1)} GB`;
}
function formatSignedGb(kb) {
    const gb = kb / 1000000;
    return `${gb >= 0 ? "+" : "-"}${Math.abs(gb).toFixed(1)}`;
}
function memoryLevelColor(rssKb, warnKb, ceilingKb) {
    if (rssKb >= ceilingKb)
        return "#d4343c";
    if (rssKb > warnKb)
        return "#d4a72c";
    return "#59bf40";
}
function bannerCard(accent, background, testId, title, body) {
    return (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Focusable, { onActivate: () => { }, children: SP_JSX.jsxs("div", { "data-testid": testId, style: {
                    padding: "8px 12px",
                    backgroundColor: background,
                    borderLeft: `3px solid ${accent}`,
                    borderRadius: "4px",
                }, children: [SP_JSX.jsx("div", { style: { fontSize: "13px", fontWeight: "bold", color: accent, marginBottom: "6px" }, children: title }), SP_JSX.jsx("div", { style: { fontSize: "12px", color: "rgba(255, 255, 255, 0.85)", lineHeight: 1.5 }, children: body })] }) }) }));
}
const SessionBudgetBanner = ({ lastAttemptStatus, syncButton, rssKb, resumeReady, restartDisabled, runDoneItems, runTotalItems, }) => {
    const paused = lastAttemptStatus === "paused";
    const highHeap = rssKb != null && rssKb > HIGH_HEAP_KB;
    if (!paused && !highHeap)
        return null;
    const memoryFreedForResume = paused && resumeReady === true;
    const liveReadingSuffix = rssKb != null ? ` (${formatGb(rssKb)})` : "";
    const progressSentence = syncButton.resumes && runDoneItems != null && runTotalItems != null && runTotalItems > 0
        ? ` ${runDoneItems} of ${runTotalItems} games done.`
        : "";
    const pressInstruction = syncButton.resumes
        ? `Press ${syncButton.label} to continue.`
        : `Press ${syncButton.label} to start over.`;
    const pausedBody = memoryFreedForResume
        ? `Steam memory is free again${liveReadingSuffix}.${progressSentence} ${pressInstruction}`
        : `Steam memory is full${liveReadingSuffix}.${progressSentence} Restart Steam, then ${syncButton.label}.`;
    const card = paused
        ? bannerCard("#3d9df6", "rgba(61, 157, 246, 0.15)", "budget-paused-banner", "Sync paused", pausedBody)
        : bannerCard("#d4a72c", "rgba(212, 167, 44, 0.15)", "budget-high-heap-banner", "Steam memory is high", `Steam memory is high: ${formatGb(rssKb)} of 2.4 GB — restart Steam before further large syncs.`);
    const gameRunning = isAnyAppRunning();
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [card, !memoryFreedForResume && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: restartSteam, disabled: (restartDisabled ?? false) || gameRunning, description: gameRunning ? "Close your running game first — restarting Steam would close it." : undefined, children: "Restart Steam now" }) }))] }));
};

const Columns = ({ columns }) => (SP_JSX.jsx(DFL.Focusable, { "flow-children": "vertical", style: { display: "flex", flexDirection: "column", gap: "12px", height: "100%", minHeight: 0 }, children: columns.map((column) => (SP_JSX.jsx(ScrollRegion, { style: { flex: "0 0 auto", width: "100%", minWidth: 0, height: "auto" }, children: column.content }, `${column.id}:${column.regionKey ?? ""}`))) }));

const SYNC_TABLE_REGISTER = {
    rowPadding: `2px ${PANE_GUTTER}`,
    headerPadding: `0 ${PANE_GUTTER} 3px`,
    rowFont: "12px",
    rowLineHeight: 1.25,
    rule: true,
};
const numericStyle = { textAlign: "right", fontVariantNumeric: "tabular-nums" };
const splitNumeric = (cells, numericFrom) => cells.map((content, index) => (index >= numericFrom ? { content, style: numericStyle } : { content }));
const TableHeader = ({ columns, cells, numericFrom, }) => SP_JSX.jsx(PaneTableHeader, { columns: columns, cells: splitNumeric(cells, numericFrom), register: SYNC_TABLE_REGISTER });
const TableRow = ({ columns, cells, numericFrom, subline, style, testId }) => (SP_JSX.jsx(PaneTableRow, { columns: columns, cells: splitNumeric(cells, numericFrom), register: SYNC_TABLE_REGISTER, ...(style === undefined ? {} : { style }), ...(testId === undefined ? {} : { testId }), children: subline !== undefined && (SP_JSX.jsx("div", { title: subline, style: {
            fontSize: SECONDARY_FONT,
            color: MUTED,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
        }, children: subline })) }));
const PaneRow = ({ children }) => (SP_JSX.jsx("div", { style: { padding: `2px ${PANE_GUTTER} 4px` }, children: children }));
const InlineBar = ({ fraction }) => (SP_JSX.jsx("div", { "data-testid": "unit-bar", style: { height: "4px", borderRadius: "2px", background: "rgba(255, 255, 255, 0.12)", marginTop: "3px" }, children: SP_JSX.jsx("div", { style: {
            height: "100%",
            borderRadius: "2px",
            width: `${Math.max(0, Math.min(100, fraction * 100))}%`,
            background: "#1a9fff",
        } }) }));

const PREVIEW_COLUMNS = "minmax(0, 1fr) 52px 62px 68px";
const LONG_SYNC_HINT_THRESHOLD_SEC = 600;
function isFullResync(s) {
    const platforms = s.sync_platform_count ?? 0;
    return platforms > 0 && (s.restamp_platform_count ?? 0) === platforms && s.changed_count > 0;
}
function formatSyncScope(s) {
    const parts = [];
    if ((s.sync_platform_count ?? 0) > 0)
        parts.push(pluralize(s.sync_platform_count ?? 0, "platform"));
    if ((s.sync_collection_count ?? 0) > 0)
        parts.push(pluralize(s.sync_collection_count ?? 0, "collection"));
    return parts.join(" · ");
}
function emptyPreviewSentence(s, hasChanges) {
    if (!hasChanges)
        return "Everything is up to date.";
    const covers = s.cover_refresh_count ?? 0;
    if (covers > 0)
        return `No shortcut changes — ${pluralize(covers, "cover update")}.`;
    if ((s.restamp_platform_count ?? 0) > 0)
        return "No changes — finishing a previous sync.";
    return "No shortcut changes — there is still something to apply.";
}
function addedRemovedLine(added, removed) {
    const parts = [];
    if (added !== null)
        parts.push(`Added: ${added}`);
    if (removed !== null)
        parts.push(`Removed: ${removed}`);
    return parts.length > 0 ? parts.join(" · ") : null;
}
function collectionNames(s) {
    const diff = s.collection_diff;
    if (!diff)
        return null;
    return addedRemovedLine(diff.added.length > 0 ? diff.added.join(", ") : null, diff.removed.length > 0 ? diff.removed.join(", ") : null);
}
function platformCollectionCounts(s) {
    const diff = s.platform_collection_diff;
    if (!diff)
        return null;
    return addedRemovedLine(diff.added_count > 0 ? String(diff.added_count) : null, diff.removed_count > 0 ? String(diff.removed_count) : null);
}
function deadlineNote(expired, secondsLeft) {
    if (expired)
        return { note: "expired", noteColor: AMBER };
    if (secondsLeft === null)
        return {};
    return { note: `expires in ${formatTimeRemaining(secondsLeft)}` };
}
const NOT_SYNCED_NOTE = "not synced as a platform";
const NO_COUNT = "—";
function collectionChangeLine(s) {
    const parts = [];
    const added = s.collection_diff?.added.length ?? 0;
    const removed = s.collection_diff?.removed.length ?? 0;
    if (added > 0)
        parts.push(`${pluralize(added, "collection")} added`);
    if (removed > 0)
        parts.push(`${pluralize(removed, "collection")} removed`);
    const platform = (s.platform_collection_diff?.added_count ?? 0) + (s.platform_collection_diff?.removed_count ?? 0);
    if (platform > 0)
        parts.push(`${pluralize(platform, "platform collection")} changed`);
    return parts.length > 0 ? `plus ${parts.join(", ")}` : null;
}
const PreviewPanel = ({ state, preview }) => {
    const summary = preview.summary;
    const breakdown = summary.platform_breakdown;
    const names = collectionNames(summary);
    const platformCollections = platformCollectionCounts(summary);
    const totals = [summary.new_count, summary.changed_count, summary.remove_count];
    const hasCollectionsRow = names !== null;
    const hasPlatformCollectionsRow = summary.platform_collection_diff?.has_changes === true;
    const showTable = totals[0] + totals[1] + totals[2] > 0 || hasCollectionsRow || hasPlatformCollectionsRow;
    const hasChanges = previewHasChanges(preview);
    const beyondTheColumns = collectionChangeLine(summary);
    const applySeconds = previewApplySeconds(summary);
    const scopeText = formatSyncScope(summary);
    const secondsLeft = state.previewSecondsLeft;
    const expired = state.previewExpired;
    const hintText = "Progress is saved about every 200 games — cancelling is safe." +
        (applySeconds >= LONG_SYNC_HINT_THRESHOLD_SEC ? " Long syncs pause during sleep; keep the Deck powered." : "");
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(SectionTitle, { title: "Preview", ...deadlineNote(expired, secondsLeft) }), isFullResync(summary) && SP_JSX.jsx(Muted, { children: "Full re-sync \u2014 all platforms re-fetched." }), expired && SP_JSX.jsx(Muted, { children: "This preview is too old to apply. Refresh works out a fresh one." }), SP_JSX.jsxs(ButtonRow, { padding: "4px 16px 8px", children: [SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: state.busy || expired || !hasChanges, onClick: state.applyPreview, children: "Apply Sync" }), SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: state.busy, onClick: state.refreshPreview, children: "Refresh" }), SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: state.busy, onClick: state.cancelPreview, children: "Cancel" })] }), showTable ? (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(TableHeader, { columns: PREVIEW_COLUMNS, cells: ["Platform", "New", "Updated", "Removed"], numericFrom: 1 }), breakdown === undefined ? (SP_JSX.jsx(Muted, { children: "Your server did not send the per-platform split, so only the totals are shown." })) : (breakdown.map((row) => (SP_JSX.jsx(PreviewRow, { columns: PREVIEW_COLUMNS, name: row.name, inlineNote: row.synced ? undefined : NOT_SYNCED_NOTE, counts: [row.new_count, row.changed_count, row.remove_count] }, row.slug)))), hasCollectionsRow && SP_JSX.jsx(PreviewRow, { columns: PREVIEW_COLUMNS, name: "Collections", subline: names }), hasPlatformCollectionsRow && (SP_JSX.jsx(PreviewRow, { columns: PREVIEW_COLUMNS, name: "Platform collections", subline: platformCollections ?? undefined })), SP_JSX.jsx(PreviewRow, { columns: PREVIEW_COLUMNS, name: "Total", counts: totals, total: true }), beyondTheColumns !== null && SP_JSX.jsx(Muted, { children: beyondTheColumns })] })) : (SP_JSX.jsx(Muted, { children: emptyPreviewSentence(summary, hasChanges) })), hasChanges && (SP_JSX.jsx(PaneRow, { children: SP_JSX.jsxs("span", { style: { fontSize: SECONDARY_FONT, color: MUTED }, children: [scopeText ? `Syncing ${scopeText} · ` : "", `estimated duration ${formatDuration(applySeconds)}`] }) })), hasChanges && SP_JSX.jsx(Muted, { children: hintText }), preview.pause_likely === true && (SP_JSX.jsx("div", { "data-testid": "budget-advisory", style: {
                    fontSize: SECONDARY_FONT,
                    color: "#7fbcff",
                    borderLeft: "3px solid rgba(61, 157, 246, 0.6)",
                    padding: "2px 8px",
                    margin: "2px 16px 6px",
                    lineHeight: 1.4,
                }, children: "Will likely pause partway to protect Steam's memory \u2014 normal for large syncs. Restart Steam when prompted, then resume." })), state.status !== null && SP_JSX.jsx(Muted, { children: state.status })] }));
};
const PreviewRow = ({ columns, name, inlineNote, subline, counts, total }) => {
    const label = (SP_JSX.jsxs("span", { title: inlineNote ? `${name} · ${inlineNote}` : name, style: { fontWeight: total ? 600 : 400 }, children: [name, inlineNote && SP_JSX.jsx("span", { style: { color: MUTED }, children: ` · ${inlineNote}` })] }));
    const countCells = counts
        ? [
            SP_JSX.jsx(CountCell, { value: counts[0], bold: total ?? false }, "new"),
            SP_JSX.jsx(CountCell, { value: counts[1], bold: total ?? false }, "changed"),
            SP_JSX.jsx(CountCell, { value: counts[2], bold: total ?? false }, "removed"),
        ]
        : ["new", "changed", "removed"].map((column) => (SP_JSX.jsx("span", { style: { color: MUTED }, children: NO_COUNT }, column)));
    return (SP_JSX.jsx(TableRow, { columns: columns, style: total ? { borderTop: TABLE_LINE, marginTop: "2px", paddingTop: "5px" } : undefined, cells: [label, ...countCells], numericFrom: 1, subline: subline }));
};
const CountCell = ({ value, bold }) => (SP_JSX.jsx("span", { style: { color: value === 0 ? MUTED : undefined, fontWeight: bold ? 600 : 400 }, children: value }));

const RUN_COLUMNS = "minmax(0, 1.2fr) minmax(0, 1fr) minmax(0, 1fr)";
const UNIT_REGION_TESTID = "run-units";
const RUN_PANE = { display: "flex", flexDirection: "column", height: "100%", minHeight: 0 };
const UNIT_REGION = { flex: "1 1 auto", height: "auto", minHeight: 0 };
function centreRowInRegion(region, row) {
    const furthest = region.scrollHeight - region.clientHeight;
    if (furthest <= 0)
        return;
    const centred = offsetWithinScroller(row, region) + row.getBoundingClientRect().height / 2 - region.clientHeight / 2;
    region.scrollTo({ top: Math.max(0, Math.min(furthest, centred)), behavior: "smooth" });
}
const UNIT_STAGE_TEXT = {
    discovering: "starting",
    fetching: "fetching",
    applying: "applying shortcuts",
    finalizing: "finishing",
    done: "done",
    cancelled: "stopped",
    error: "stopped",
};
function unitStageText(stage) {
    return stage ? UNIT_STAGE_TEXT[stage] : "working";
}
function unitOutcome(unit) {
    const parts = [];
    if (unit.created > 0)
        parts.push(`${unit.created} added`);
    if (unit.updated > 0)
        parts.push(`${unit.updated} updated`);
    return parts.length > 0 ? parts.join(" · ") : "—";
}
function unitPlan(unit) {
    if (unit.predictedSkip)
        return "expected to skip";
    if (unit.newShortcutCount !== null && unit.newShortcutCount > 0)
        return `${unit.newShortcutCount} new`;
    return pluralize(unit.romCount, "ROM");
}
const RunPanel = ({ state }) => {
    const run = state.run;
    const stepText = run.totalSteps > 0 ? `unit ${run.step} of ${run.totalSteps}` : "";
    const noteParts = [stepText, run.etaText ?? ""].filter((part) => part !== "");
    const pane = SP_REACT.useRef(null);
    const running = state.units.find((unit) => unit.state === "running");
    const runningTestId = running ? unitTestId(running) : null;
    SP_REACT.useEffect(() => {
        const root = pane.current;
        if (root === null || runningTestId === null)
            return;
        const region = root.querySelector(`[data-testid="${UNIT_REGION_TESTID}"]`);
        const row = root.querySelector(`[data-testid="${runningTestId}"]`);
        if (region !== null && row !== null)
            centreRowInRegion(region, row);
    }, [runningTestId]);
    return (SP_JSX.jsxs("div", { ref: pane, style: RUN_PANE, children: [SP_JSX.jsx(SectionTitle, { title: "Sync running", ...(noteParts.length > 0 ? { note: noteParts.join(" · ") } : {}) }), SP_JSX.jsxs(PaneRow, { children: [SP_JSX.jsx("div", { style: { fontSize: SECONDARY_FONT, color: MUTED, paddingBottom: "4px" }, "data-testid": "run-stage", children: run.stageLabel }), SP_JSX.jsx(DFL.ProgressBar, { indeterminate: run.coarseFraction === undefined, ...(run.coarseFraction !== undefined ? { nProgress: run.coarseFraction } : {}) })] }), SP_JSX.jsx(ButtonRow, { padding: "6px 16px 4px", children: SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: state.cancelling, onClick: state.cancelRun, children: state.cancelling ? "Cancelling…" : "Cancel Sync" }) }), state.units.length === 0 ? (SP_JSX.jsx(Muted, { children: run.hasFineDetail ? run.fineDetailText : "Per-unit detail is not available for this run." })) : (SP_JSX.jsxs(ScrollRegion, { testId: UNIT_REGION_TESTID, style: UNIT_REGION, children: [SP_JSX.jsx(TableHeader, { columns: RUN_COLUMNS, cells: ["Unit", "Status", "Result"], numericFrom: 2 }), state.units.map((unit) => (SP_JSX.jsx(RunUnitRow, { unit: unit, state: state }, `${unit.type}:${unit.id}`)))] })), state.status !== null && SP_JSX.jsx(Muted, { children: state.status })] }));
};
function unitTestId(unit) {
    return `run-unit-${unit.type}-${unit.id}`;
}
const RunUnitRow = ({ unit, state }) => {
    const nameCell = (SP_JSX.jsxs("span", { title: unit.type === "collection" ? `${unit.name} · collection` : unit.name, children: [unit.name, unit.type === "collection" && SP_JSX.jsx("span", { style: { color: MUTED }, children: " \u00B7 collection" })] }));
    let status;
    let result;
    if (unit.state === "done") {
        status = SP_JSX.jsx("span", { style: { color: GREEN }, children: "done" });
        result = unitOutcome(unit);
    }
    else if (unit.state === "running") {
        status = (SP_JSX.jsxs("span", { children: [unitStageText(state.run.stage), SP_JSX.jsx(InlineBar, { fraction: state.run.withinUnitFraction })] }));
        result = unitOutcome(unit);
    }
    else {
        status = SP_JSX.jsx("span", { style: { color: MUTED }, children: "waiting" });
        result = unitPlan(unit);
    }
    return (SP_JSX.jsx(TableRow, { columns: RUN_COLUMNS, numericFrom: 2, testId: unitTestId(unit), cells: [
            nameCell,
            status,
            SP_JSX.jsx("span", { style: { color: unit.state === "waiting" ? MUTED : undefined }, children: result }, "result"),
        ] }));
};

const RUN_STATUS_COLOR = {
    running: undefined,
    completed: GREEN,
    paused: AMBER,
    cancelled: MUTED,
    interrupted: AMBER,
    errored: RED,
};
function formatRunStart(iso) {
    const started = new Date(iso);
    if (Number.isNaN(started.getTime()))
        return iso;
    const time = started.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
    const now = new Date();
    const sameDay = (a, b) => a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
    if (sameDay(started, now))
        return `Today ${time}`;
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (sameDay(started, yesterday))
        return `Yesterday ${time}`;
    return `${started.toLocaleDateString(undefined, { month: "short", day: "numeric" })} ${time}`;
}
function formatRunCoverage(run) {
    const platforms = run.platforms_completed;
    if (platforms === null) {
        return run.platforms_planned > 0 ? `${pluralize(run.platforms_planned, "platform")} planned` : "nothing recorded";
    }
    const parts = [];
    if (run.platforms_planned > 0 || platforms.length > 0) {
        parts.push(platforms.length === run.platforms_planned
            ? pluralize(platforms.length, "platform")
            : `${platforms.length} of ${run.platforms_planned} platforms`);
    }
    const collections = run.collections_completed;
    if (collections !== null && collections.length > 0)
        parts.push(pluralize(collections.length, "collection"));
    return parts.length > 0 ? parts.join(" · ") : "nothing completed";
}
const ControlRow = ({ label, value, subline, testId }) => (SP_JSX.jsxs(DFL.Focusable, { onActivate: () => { }, "data-testid": testId, style: { padding: "4px 16px" }, children: [SP_JSX.jsxs("div", { style: { display: "flex", alignItems: "baseline", gap: "8px" }, children: [SP_JSX.jsx("span", { style: { flex: "1 1 auto", minWidth: 0, overflow: "hidden", textOverflow: "ellipsis" }, children: label }), SP_JSX.jsx("span", { style: { flex: "0 0 auto", fontSize: SECONDARY_FONT, fontVariantNumeric: "tabular-nums" }, children: value })] }), subline !== undefined && (SP_JSX.jsx("div", { title: subline, style: {
                fontSize: SECONDARY_FONT,
                color: MUTED,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
            }, children: subline }))] }));
const SyncControls = ({ state }) => (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(OptionsSection, { state: state }), SP_JSX.jsx(MemorySection, { state: state }), SP_JSX.jsx(RunsSection, { state: state })] }));
function nothingToClear(stats, statsFailed) {
    if (stats !== null)
        return !stats.last_sync && !stats.last_attempt;
    return !statsFailed;
}
function forceFullSyncNote(state) {
    if (state.run.running)
        return "Not while a run is in flight.";
    if (state.fullSyncCleared !== null)
        return `${state.fullSyncCleared}. Pressing again would clear nothing.`;
    if (state.stats === null) {
        return state.statsFailed
            ? "Could not read what has already been synced — this still clears it."
            : "Reading what has already been synced…";
    }
    if (nothingToClear(state.stats, state.statsFailed))
        return "Nothing has been synced yet, so there is nothing to forget.";
    return "Forgets what was synced and rebuilds everything next run.";
}
const OptionsSection = ({ state }) => {
    const running = state.run.running;
    const disabled = running || state.fullSyncCleared !== null || nothingToClear(state.stats, state.statsFailed);
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(SectionTitle, { title: "Options" }), SP_JSX.jsx("div", { style: { padding: "0 16px" }, children: SP_JSX.jsx(DFL.ToggleField, { label: "Skip preview", description: "Start the sync without asking first.", checked: state.skipPreview, bottomSeparator: "none", onChange: state.setSkipPreview }) }), SP_JSX.jsx("div", { style: { padding: "6px 16px 0" }, children: SP_JSX.jsx(DFL.DialogButton, { style: { width: "100%", minWidth: 0, padding: "6px 10px", fontSize: "13px", color: RED }, disabled: disabled, onClick: () => DFL.showModal(SP_JSX.jsx(DFL.ConfirmModal, { strTitle: "Force a full re-sync?", strDescription: "This forgets what has already been synced, so the next run re-fetches every platform and rewrites every shortcut. Your games stay in Steam \u2014 only the plugin's record of what is already correct is cleared, which is also what a resume would have continued from.", strOKButtonText: "Force Full Sync", strCancelButtonText: "Cancel", onOK: state.forceFullSync })), children: "Force Full Sync" }) }), SP_JSX.jsx(Muted, { children: forceFullSyncNote(state) }), state.optionsStatus !== null && SP_JSX.jsx(Muted, { children: state.optionsStatus })] }));
};
const MemorySection = ({ state }) => {
    const budget = state.budget;
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(SectionTitle, { title: "Steam memory" }), SP_JSX.jsx(ControlRow, { label: "Now", testId: "memory-now", value: budget?.rss_kb == null ? (SP_JSX.jsx("span", { style: { color: MUTED }, children: "unavailable" })) : (SP_JSX.jsx("span", { style: { color: memoryLevelColor(budget.rss_kb, budget.warn_kb, budget.ceiling_kb) }, children: formatGb(budget.rss_kb) })) }), SP_JSX.jsx(ControlRow, { label: "Last run", testId: "memory-last-run", value: budget?.memory_delta_kb == null ? (SP_JSX.jsx("span", { style: { color: MUTED }, children: "not recorded" })) : (SP_JSX.jsx("span", { style: { color: MUTED }, children: formatSignedGb(budget.memory_delta_kb) })) })] }));
};
const RunsSection = ({ state }) => (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(SectionTitle, { title: "Last runs" }), state.runsFailed && SP_JSX.jsx(Muted, { children: "Could not read the run history. Open the page again to try." }), state.runsLoading && state.runs.length === 0 && !state.runsFailed && SP_JSX.jsx(Muted, { children: "Reading the run history\u2026" }), !state.runsLoading && !state.runsFailed && state.runs.length === 0 && SP_JSX.jsx(Muted, { children: "No sync has run yet." }), state.runs.map((run) => (SP_JSX.jsx(ControlRow, { testId: `run-${run.id}`, label: formatRunStart(run.started_at), value: SP_JSX.jsx("span", { style: { color: RUN_STATUS_COLOR[run.status] }, children: run.status }), subline: run.error === null ? formatRunCoverage(run) : `${formatRunCoverage(run)} · ${run.error}` }, run.id)))] }));

const PREVIEW_LABEL = "Check for changes";
function startButtonLabel(resume, skipPreview) {
    return skipPreview ? resume.label : PREVIEW_LABEL;
}
function formatResumeScope(resumableGames) {
    return `${pluralize(resumableGames, "game")} already synced — a resume continues from there.`;
}
function syncResumeState(stats) {
    const status = stats?.last_attempt?.status;
    const incompleteAttempt = status === "interrupted" || status === "cancelled" || status === "paused";
    const resumableGames = stats?.resumable_games ?? 0;
    const skipAuthoritySurvives = resumableGames > 0 || (stats?.has_completion_stamp ?? false);
    const canResume = incompleteAttempt && (stats?.roms ?? 0) > 0 && skipAuthoritySurvives;
    return {
        canResume,
        label: canResume ? "Resume Sync" : "Sync Library",
        scopeText: canResume && resumableGames > 0 ? formatResumeScope(resumableGames) : null,
    };
}

const PREVIEW_FAILED = "Could not work out what would change. Check the connection to RomM and try again.";
const FULL_SYNC_CLEARED = "The next sync will re-fetch and re-apply everything";
const BUDGET_POLL_RUNNING_MS = 5000;
const BUDGET_POLL_PAUSED_MS = 10000;
function clearRunUnitsUnlessResuming() {
    if (!syncResumeState(getSyncStatsSnapshot()).canResume)
        clearRunUnits();
}
function primaryActionFor(preview, expired, resume, startLabel) {
    if (preview === null)
        return { label: startLabel, resumes: resume.canResume };
    if (!expired && previewHasChanges(preview))
        return { label: "Apply Sync", resumes: resume.canResume };
    return { label: "Refresh", resumes: resume.canResume };
}
function useSyncPage() {
    const preview = usePendingPreview();
    const stats = useSyncStats();
    const statsFailed = useSyncStatsFailed();
    const budget = useSessionBudget();
    const units = useRunUnits();
    const run = useSyncRunView();
    const running = run.running;
    const [nowMs, setNowMs] = SP_REACT.useState(null);
    const [skipPreview, setSkipPreviewState] = SP_REACT.useState(false);
    const [busy, setBusy] = SP_REACT.useState(false);
    const [cancellingRunId, setCancellingRunId] = SP_REACT.useState(null);
    const [status, setStatus] = SP_REACT.useState(null);
    const [optionsStatus, setOptionsStatus] = SP_REACT.useState(null);
    const [fullSyncCleared, setFullSyncCleared] = SP_REACT.useState(null);
    const [runs, setRuns] = SP_REACT.useState([]);
    const [runsLoading, setRunsLoading] = SP_REACT.useState(true);
    const [runsFailed, setRunsFailed] = SP_REACT.useState(false);
    const loadRuns = SP_REACT.useCallback(async () => {
        setRunsLoading(true);
        try {
            const answer = await getSyncRuns();
            if (!answer.success) {
                setRunsFailed(true);
                return;
            }
            setRunsFailed(false);
            setRuns(answer.runs);
        }
        catch {
            setRunsFailed(true);
        }
        finally {
            setRunsLoading(false);
        }
    }, []);
    const computePreview = SP_REACT.useCallback(async (discardPending) => {
        setBusy(true);
        setStatus(null);
        resetSyncCancel();
        setCancellingRunId(null);
        if (discardPending) {
            clearPendingPreview();
            try {
                await syncCancelPreview();
            }
            catch (e) {
                logError(`Failed to discard the pending preview before refreshing it: ${e}`);
            }
        }
        clearRunUnitsUnlessResuming();
        setSyncProgress({ running: true, stage: "fetching", message: "Fetching library...", runKind: "preview" });
        try {
            await reconcileStaleShortcuts();
            const result = await syncPreview();
            if (!result.success) {
                setSyncProgress({ running: false, stage: "" });
                setStatus(result.message || PREVIEW_FAILED);
                return;
            }
            if (isCancelRequested()) {
                resetSyncCancel();
                detach(syncCancelPreview());
                setSyncProgress({ running: false, stage: "" });
                setStatus("Sync cancelled");
                return;
            }
            setNowMs(Date.now());
            adoptPreview(result);
            setSyncProgress({ running: false, stage: "" });
        }
        catch {
            setSyncProgress({ running: false, stage: "" });
            setStatus(PREVIEW_FAILED);
        }
        finally {
            setBusy(false);
        }
    }, []);
    const applyPreview = SP_REACT.useCallback(async () => {
        const pending = getPendingPreviewSnapshot();
        if (!pending)
            return;
        if (previewSecondsLeft(pending, Date.now()) === 0) {
            setNowMs(Date.now());
            return;
        }
        const previewId = pending.preview_id;
        const etaSeconds = previewApplySeconds(pending.summary);
        resetSyncCancel();
        clearPendingPreview();
        setStatus(null);
        setCancellingRunId(null);
        setBusy(true);
        clearRunUnitsUnlessResuming();
        setSyncProgress({
            running: true,
            stage: "applying",
            message: "Applying changes...",
            etaSeconds,
            runKind: "apply",
        });
        try {
            const result = await syncApplyDelta(previewId);
            if (!result.success) {
                setSyncProgress({ running: false, stage: "" });
                setStatus(result.message || "Could not apply the preview.");
            }
        }
        catch {
            setSyncProgress({ running: false, stage: "" });
            setStatus("Failed to apply sync");
        }
        finally {
            setBusy(false);
        }
    }, []);
    const cancelPreview = SP_REACT.useCallback(async () => {
        clearPendingPreview();
        setStatus(null);
        try {
            await syncCancelPreview();
        }
        catch (e) {
            logError(`Failed to discard the pending preview: ${e}`);
        }
    }, []);
    const cancelRun = SP_REACT.useCallback(async () => {
        const runId = getSyncProgress().runId ?? "";
        setCancellingRunId(runId);
        requestSyncCancel();
        try {
            await cancelSync(runId);
        }
        catch {
            setCancellingRunId(null);
            setStatus("Failed to cancel sync");
        }
    }, []);
    const changeSkipPreview = SP_REACT.useCallback(async (value) => {
        setSkipPreviewState(value);
        setOptionsStatus(null);
        try {
            const result = await saveSkipPreview(value);
            if (!result.success) {
                setSkipPreviewState(!value);
                setOptionsStatus("Could not save that; the setting was put back.");
            }
        }
        catch {
            setSkipPreviewState(!value);
            setOptionsStatus("Could not save that; the setting was put back.");
        }
    }, []);
    const forceFullSync = SP_REACT.useCallback(async () => {
        setOptionsStatus(null);
        try {
            const result = await clearSyncCache();
            if (!result.success) {
                setOptionsStatus(result.message || "Could not clear the sync cache.");
                return;
            }
            setFullSyncCleared(result.message || FULL_SYNC_CLEARED);
            clearPendingPreview();
            try {
                await syncCancelPreview();
            }
            catch (e) {
                logError(`Failed to discard the pending preview after a full-sync clear: ${e}`);
            }
        }
        catch {
            setOptionsStatus("Failed to clear sync cache");
        }
        finally {
            detach(refreshSyncStatsAfterChange());
        }
    }, []);
    const startRunDirectly = SP_REACT.useCallback(async () => {
        setBusy(true);
        setStatus(null);
        resetSyncCancel();
        setCancellingRunId(null);
        clearRunUnitsUnlessResuming();
        setSyncProgress({ running: true, stage: "fetching", message: "Fetching library...", runKind: "apply" });
        try {
            await reconcileStaleShortcuts();
            const result = await startSync();
            if (!result.success) {
                setSyncProgress({ running: false, stage: "" });
                setStatus(result.message || "Could not start the sync.");
            }
        }
        catch {
            setSyncProgress({ running: false, stage: "" });
            setStatus("Failed to start sync");
        }
        finally {
            setBusy(false);
        }
    }, []);
    const startPreview = () => {
        if (skipPreview) {
            detach(startRunDirectly());
            return;
        }
        detach(computePreview(false));
    };
    SP_REACT.useEffect(() => {
        detach(loadRuns());
        detach(refreshSyncStats());
        detach(refreshSessionBudget());
        detach(refreshPendingPreview().then(() => setNowMs(Date.now())));
        getSettings()
            .then((s) => setSkipPreviewState(s.skip_preview ?? false))
            .catch((e) => logError(`Failed to read the skip-preview setting: ${e}`));
    }, [loadRuns]);
    const terminal = isTerminalStage(run.stage);
    const wasRunning = SP_REACT.useRef(running);
    SP_REACT.useEffect(() => {
        if (wasRunning.current && !running && terminal) {
            detach(loadRuns());
            detach(refreshSyncStatsAfterChange());
            detach(refreshSessionBudgetAfterChange());
            setFullSyncCleared(null);
        }
        wasRunning.current = running;
    }, [running, terminal, loadRuns]);
    const lastRunPaused = stats?.last_attempt?.status === "paused";
    SP_REACT.useEffect(() => {
        if (!running && !lastRunPaused)
            return;
        const id = setInterval(() => {
            detach(refreshSessionBudget());
            if (!running)
                detach(refreshSyncStats());
        }, running ? BUDGET_POLL_RUNNING_MS : BUDGET_POLL_PAUSED_MS);
        return () => clearInterval(id);
    }, [running, lastRunPaused]);
    const previewDeadline = preview?.expires_at;
    SP_REACT.useEffect(() => {
        if (previewDeadline === undefined)
            return;
        const id = setInterval(() => setNowMs(Date.now()), PREVIEW_COUNTDOWN_TICK_MS);
        return () => clearInterval(id);
    }, [previewDeadline]);
    const secondsLeft = preview === null || nowMs === null ? null : previewSecondsLeft(preview, nowMs);
    const resume = syncResumeState(stats);
    const startLabel = startButtonLabel(resume, skipPreview);
    const previewExpired = secondsLeft === 0;
    const cancelling = cancellingRunId !== null && running && (cancellingRunId === "" || cancellingRunId === run.runId);
    return {
        preview,
        previewSecondsLeft: secondsLeft,
        previewExpired,
        run,
        units,
        stats,
        statsFailed,
        budget,
        resume,
        startLabel,
        primaryAction: primaryActionFor(preview, previewExpired, resume, startLabel),
        busy,
        cancelling,
        status,
        optionsStatus,
        skipPreview,
        fullSyncCleared,
        runs,
        runsLoading,
        runsFailed,
        startPreview,
        applyPreview: () => detach(applyPreview()),
        refreshPreview: () => detach(computePreview(true)),
        cancelPreview: () => detach(cancelPreview()),
        cancelRun: () => detach(cancelRun()),
        setSkipPreview: (value) => detach(changeSkipPreview(value)),
        forceFullSync: () => detach(forceFullSync()),
    };
}

const CONTROLS_WIDTH = "270px";
const SyncPage = ({ onBack }) => {
    const state = useSyncPage();
    return (SP_JSX.jsx(WidePage, { title: "Sync", onBack: onBack, ownRegions: true, children: SP_JSX.jsx(Columns, { columns: [
                { id: "run", content: SP_JSX.jsx(SyncMainColumn, { state: state }) },
                { id: "controls", width: CONTROLS_WIDTH, content: SP_JSX.jsx(SyncControls, { state: state }) },
            ] }) }));
};
const BODY_BOX = { display: "contents" };
const SyncMainColumn = ({ state }) => {
    const bodyBox = SP_REACT.useRef(null);
    let body;
    let bodyKind;
    if (state.run.running) {
        body = SP_JSX.jsx(RunPanel, { state: state });
        bodyKind = "run";
    }
    else if (state.preview !== null) {
        body = SP_JSX.jsx(PreviewPanel, { state: state, preview: state.preview });
        bodyKind = "preview";
    }
    else {
        body = SP_JSX.jsx(IdlePanel, { state: state });
        bodyKind = "idle";
    }
    useEntryFocusOnBodySwap(bodyBox, bodyKind);
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [!state.run.running && (SP_JSX.jsx(SessionBudgetBanner, { lastAttemptStatus: state.stats?.last_attempt?.status, syncButton: state.primaryAction, rssKb: state.budget?.rss_kb ?? null, resumeReady: state.budget?.resume_ready ?? null, runDoneItems: state.budget?.run_done_items ?? null, runTotalItems: state.budget?.run_total_items ?? null })), SP_JSX.jsx("div", { ref: bodyBox, style: BODY_BOX, children: body })] }));
};
const IdlePanel = ({ state }) => (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(SectionTitle, { title: "Preview" }), SP_JSX.jsx(Muted, { children: state.skipPreview
                ? `Nothing is waiting to be applied. Skip preview is on, so ${state.startLabel} applies changes without showing them first.`
                : "Nothing is waiting to be applied. Start a preview to see what would change." }), SP_JSX.jsx(ButtonRow, { padding: "4px 16px", children: SP_JSX.jsx(DFL.DialogButton, { style: FLAT_BUTTON, disabled: state.busy, onClick: state.startPreview, children: state.startLabel }) }), state.resume.scopeText !== null && SP_JSX.jsx(Muted, { children: state.resume.scopeText }), state.status !== null && SP_JSX.jsx(Muted, { children: state.status })] }));

const REMOVAL_REPORT_TIMEOUT_MS = 15000;
const DANGER_ZONE_LEASE_OWNER = "danger-zone";
const DEFAULT_WHITELIST_PATTERNS = [
    "retrodeck",
    "moonlight",
    "chiaki",
    "chrome",
    "chromium",
    "firefox",
    "vivaldi",
    "heroic",
    "lutris",
    "bottles",
    "protonup",
    "emudeck",
    "desktop mode",
    "return to gaming mode",
    "nonsteamlaunchers",
];
const SETTLE_POLL_MS = 250;
const SETTLE_TIMEOUT_MS = 3000;
const readShortcutStoreSize = () => {
    if (typeof collectionStore === "undefined")
        return null;
    const apps = collectionStore.deckDesktopApps?.apps;
    return apps ? apps.size : null;
};
async function recountAfterStoreSettles(removedCount, loadNonSteamApps) {
    const baseline = readShortcutStoreSize();
    if (baseline !== null && removedCount > 0) {
        const target = Math.max(0, baseline - removedCount);
        const deadline = Date.now() + SETTLE_TIMEOUT_MS;
        for (;;) {
            const size = readShortcutStoreSize();
            if (size === null || size <= target || Date.now() >= deadline)
                break;
            await new Promise((resolve) => setTimeout(resolve, SETTLE_POLL_MS));
        }
    }
    loadNonSteamApps();
}
const ShortcutRemovalSection = ({ loadNonSteamApps, status, setStatus, busy, runRemoval, }) => {
    const [uninstallStatus, setUninstallStatus] = SP_REACT.useState("");
    const [confirmRemoveAllRomm, setConfirmRemoveAllRomm] = SP_REACT.useState(false);
    const [confirmUninstall, setConfirmUninstall] = SP_REACT.useState(false);
    const syncRunning = useSyncRunning();
    const removalDisabled = busy || syncRunning;
    const handleRemoveAllRomm = async () => {
        if (!confirmRemoveAllRomm) {
            setConfirmRemoveAllRomm(true);
            return;
        }
        setConfirmRemoveAllRomm(false);
        await runRemoval(async (onProgress) => {
            setStatus("Removing all shortcuts...");
            let removedCount = 0;
            const admission = capturePruneLeaseAdmission(DANGER_ZONE_LEASE_OWNER);
            try {
                const result = await removeAllShortcuts();
                if (!result.success) {
                    setStatus(result.message ?? "Failed to remove shortcuts");
                }
                else {
                    const backendAppIds = result.app_ids ?? [];
                    const removed = new Set(backendAppIds);
                    await withPruneLease(result.prune_lease_token, "All-shortcut removal", async (signal) => {
                        await removeShortcutsPaced(backendAppIds, onProgress, signal);
                        if (isPruneLeaseCancelled(signal))
                            return;
                        const liveAppIds = await getLiveRomMShortcutAppIds();
                        if (isPruneLeaseCancelled(signal))
                            return;
                        if (liveAppIds === null) {
                            logWarn("Live RomM shortcut scan unavailable — removed backend-bound shortcuts only.");
                        }
                        else {
                            const orphans = liveAppIds.filter((appId) => !removed.has(appId));
                            logInfo(`Remove-all: ${orphans.length} live-scanned RomM shortcut(s) were not in the backend list.`);
                            await removeShortcutsPaced(orphans, (done, orphanTotal) => onProgress(backendAppIds.length + done, backendAppIds.length + orphanTotal), signal);
                            if (isPruneLeaseCancelled(signal))
                                return;
                            for (const appId of orphans)
                                removed.add(appId);
                        }
                        removedCount = removed.size;
                        await clearAllRomMCollections(signal);
                        if (isPruneLeaseCancelled(signal))
                            return;
                        if (result.rom_ids?.length || result.prune_lease_token) {
                            await withTimeout(reportRemovalResults(result.rom_ids ?? [], result.prune_lease_token ?? null), REMOVAL_REPORT_TIMEOUT_MS);
                        }
                    }, DANGER_ZONE_LEASE_OWNER, admission);
                    setStatus(result.message ?? "All shortcuts removed");
                }
            }
            catch (e) {
                if (isPruneLeaseCancellation(e, admission)) {
                    logWarn(`All-shortcut removal continuation was cancelled: ${e}`);
                    return;
                }
                setStatus("Failed to remove shortcuts");
            }
            await recountAfterStoreSettles(removedCount, loadNonSteamApps);
        });
    };
    const handleUninstallAll = async () => {
        if (!confirmUninstall) {
            setConfirmUninstall(true);
            return;
        }
        try {
            setUninstallStatus("Uninstalling...");
            const admission = capturePruneLeaseAdmission(DANGER_ZONE_LEASE_OWNER);
            const result = await uninstallAllRoms();
            if (!result.success && result.app_ids === undefined) {
                setUninstallStatus(result.message ?? "Failed to uninstall ROMs");
            }
            else {
                await withPruneLease(result.prune_lease_token, "Bulk uninstall", (signal) => batchConfirmLaunchOptions((result.app_ids ?? []).map((appId) => ({ app_id: appId, launch_options: "" })), "uninstall-all", signal), DANGER_ZONE_LEASE_OWNER, admission);
                setUninstallStatus(formatUninstallStatus(result.removed_count ?? 0, (result.errors ?? []).length));
            }
        }
        catch {
            setUninstallStatus("Failed to uninstall ROMs");
        }
        setConfirmUninstall(false);
        loadNonSteamApps();
    };
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsxs(DFL.PanelSection, { title: "Remove Shortcuts", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: () => {
                                detach(handleRemoveAllRomm());
                            }, disabled: removalDisabled, description: syncRunning ? SYNC_RUNNING_HINT : undefined, children: confirmRemoveAllRomm ? (SP_JSX.jsx("span", { style: { color: "#ff8800" }, children: "Confirm: remove all RomM shortcuts?" })) : ("Remove All RomM Shortcuts") }) }), status && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: status }) }))] }), SP_JSX.jsxs(DFL.PanelSection, { title: "Installed ROMs", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: () => {
                                detach(handleUninstallAll());
                            }, disabled: removalDisabled, description: syncRunning ? SYNC_RUNNING_HINT : undefined, children: confirmUninstall ? (SP_JSX.jsx("span", { style: { color: "#ff8800" }, children: "Confirm: delete all ROM files?" })) : ("Uninstall All Installed ROMs") }) }), confirmUninstall && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: SP_JSX.jsx("span", { style: { color: "#ff8800" }, children: "This will delete all downloaded ROM files. Shortcuts remain so you can re-download later." }) }) })), uninstallStatus && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: uninstallStatus }) }))] })] }));
};
const OrphanedGridCleanupSection = () => {
    const [confirmCleanup, setConfirmCleanup] = SP_REACT.useState(false);
    const [candidateCount, setCandidateCount] = SP_REACT.useState(0);
    const [cleanupStatus, setCleanupStatus] = SP_REACT.useState("");
    const syncRunning = useSyncRunning();
    const handleCleanup = async () => {
        const liveAppIds = getAllNonSteamShortcutAppIds();
        if (liveAppIds === null) {
            setConfirmCleanup(false);
            setCleanupStatus("Could not read Steam's shortcut list — nothing was removed.");
            return;
        }
        if (!confirmCleanup) {
            try {
                const result = await cleanupOrphanedGridImages(liveAppIds, true);
                if (!result.success) {
                    setCleanupStatus(result.message ?? "Failed to scan for orphaned images");
                    return;
                }
                const count = result.candidate_count ?? 0;
                if (count === 0) {
                    setCleanupStatus("No orphaned grid images found");
                    return;
                }
                setCandidateCount(count);
                setConfirmCleanup(true);
                setCleanupStatus("");
            }
            catch {
                setCleanupStatus("Failed to scan for orphaned images");
            }
            return;
        }
        setConfirmCleanup(false);
        try {
            const result = await cleanupOrphanedGridImages(liveAppIds, false);
            if (!result.success) {
                setCleanupStatus(result.message ?? "Failed to remove orphaned images");
                return;
            }
            const removed = result.removed_count ?? 0;
            setCleanupStatus(`Removed ${removed} orphaned image${removed === 1 ? "" : "s"}`);
        }
        catch {
            setCleanupStatus("Failed to remove orphaned images");
        }
    };
    return (SP_JSX.jsxs(DFL.PanelSection, { title: "Steam Grid Images", children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: () => {
                        detach(handleCleanup());
                    }, disabled: syncRunning, description: syncRunning ? SYNC_RUNNING_HINT : undefined, children: confirmCleanup ? (SP_JSX.jsxs("span", { style: { color: "#ff8800" }, children: ["Confirm: remove ", candidateCount, " orphaned image", candidateCount === 1 ? "" : "s", "?"] })) : ("Remove Orphaned Grid Images") }) }), confirmCleanup && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: SP_JSX.jsx("span", { style: { color: "#ff8800" }, children: "Deletes leftover Steam grid artwork whose shortcut no longer exists. Artwork of live shortcuts (including non-RomM ones) is kept." }) }) })), cleanupStatus && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: cleanupStatus }) }))] }));
};
const WhitelistSection = ({ nonSteamApps, whitelistedIds, disabledDefaults, customNames, settingsLoaded, persistWhitelist, resetRemoveConfirms, }) => {
    const [showWhitelist, setShowWhitelist] = SP_REACT.useState(false);
    const [whitelistSearch, setWhitelistSearch] = SP_REACT.useState("");
    const filteredApps = SP_REACT.useMemo(() => (whitelistSearch ? nonSteamApps.filter((app) => fuzzyMatch(whitelistSearch, app.name)) : nonSteamApps), [nonSteamApps, whitelistSearch]);
    const handleToggle = (app, checked) => {
        const matchingPattern = DEFAULT_WHITELIST_PATTERNS.find((p) => app.name.toLowerCase().includes(p));
        let newDisabled = [...disabledDefaults];
        let newCustom = [...customNames];
        if (checked) {
            if (matchingPattern && disabledDefaults.includes(matchingPattern)) {
                newDisabled = newDisabled.filter((p) => p !== matchingPattern);
            }
            else if (!matchingPattern) {
                if (!newCustom.includes(app.name)) {
                    newCustom.push(app.name);
                }
            }
        }
        else {
            if (matchingPattern) {
                if (!newDisabled.includes(matchingPattern)) {
                    newDisabled.push(matchingPattern);
                }
            }
            newCustom = newCustom.filter((n) => n !== app.name);
        }
        persistWhitelist(newDisabled, newCustom);
        resetRemoveConfirms();
    };
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: () => {
                        setShowWhitelist(!showWhitelist);
                        resetRemoveConfirms();
                    }, children: showWhitelist ? "Hide Whitelist" : `Configure Whitelist (${whitelistedIds.size} protected)` }) }), showWhitelist && !settingsLoaded && SP_JSX.jsx(LoadingRow, {}), showWhitelist && settingsLoaded && (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.TextField, { label: "Search games", value: whitelistSearch, onChange: (e) => setWhitelistSearch(e.target.value) }) }), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: `Toggle ON to protect (${filteredApps.length}/${nonSteamApps.length}):` }) }), filteredApps.map((app) => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ToggleField, { label: DEFAULT_WHITELIST_PATTERNS.some((p) => app.name.toLowerCase().includes(p))
                                ? `${app.name} (auto)`
                                : app.name, checked: whitelistedIds.has(app.appId), onChange: (checked) => handleToggle(app, checked) }) }, app.appId)))] }))] }));
};
const RetroDeckSection = ({ nonSteamApps, whitelistedIds, disabledDefaults, customNames, settingsLoaded, persistWhitelist, loadNonSteamApps, setStatus, busy, runRemoval, }) => {
    const [confirmRemoveAll, setConfirmRemoveAll] = SP_REACT.useState(false);
    const [confirmRetrodeck, setConfirmRetrodeck] = SP_REACT.useState(false);
    const resetRemoveConfirms = () => {
        setConfirmRemoveAll(false);
        setConfirmRetrodeck(false);
    };
    const retrodeckAtRisk = nonSteamApps.some((a) => !whitelistedIds.has(a.appId) && a.name.toLowerCase().includes("retrodeck"));
    const handleRemoveAll = async () => {
        if (!confirmRemoveAll) {
            setConfirmRemoveAll(true);
            return;
        }
        if (retrodeckAtRisk && !confirmRetrodeck) {
            setConfirmRetrodeck(true);
            return;
        }
        setConfirmRemoveAll(false);
        setConfirmRetrodeck(false);
        await runRemoval(async (onProgress) => {
            const toRemove = nonSteamApps.filter((a) => !whitelistedIds.has(a.appId));
            setStatus(`Removing ${toRemove.length} non-steam games...`);
            await removeShortcutsPaced(toRemove.map((a) => a.appId), onProgress);
            setStatus(`Removed ${toRemove.length} non-steam game${toRemove.length === 1 ? "" : "s"}`);
            await recountAfterStoreSettles(toRemove.length, loadNonSteamApps);
        });
    };
    const removeButtonLabel = () => {
        if (confirmRetrodeck) {
            return (SP_JSX.jsx("span", { style: { color: "#ff4444", fontWeight: "bold" }, children: "!! RETRODECK WILL BE REMOVED !! Click to confirm" }));
        }
        if (confirmRemoveAll) {
            if (retrodeckAtRisk) {
                return (SP_JSX.jsxs("span", { style: { color: "#ff8800" }, children: ["WARNING: RetroDECK not protected! Remove ", nonSteamApps.length - whitelistedIds.size, " games?"] }));
            }
            return `Are you sure? Remove ${nonSteamApps.length - whitelistedIds.size} games (${whitelistedIds.size} whitelisted)?`;
        }
        const remaining = nonSteamApps.length - whitelistedIds.size;
        const excluded = whitelistedIds.size > 0 ? ` (${whitelistedIds.size} excluded)` : "";
        return `Remove ${remaining} Non-Steam Games${excluded}`;
    };
    return (SP_JSX.jsx(DFL.PanelSection, { title: "Remove Non-Steam Games", children: nonSteamApps.length === 0 ? (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "No non-steam games found" }) })) : (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", disabled: busy, onClick: () => {
                            detach(handleRemoveAll());
                        }, children: removeButtonLabel() }) }), confirmRetrodeck && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: SP_JSX.jsx("span", { style: { color: "#ff4444" }, children: "RetroDECK is NOT in the whitelist and will be permanently removed!" }) }) })), SP_JSX.jsx(WhitelistSection, { nonSteamApps: nonSteamApps, whitelistedIds: whitelistedIds, disabledDefaults: disabledDefaults, customNames: customNames, settingsLoaded: settingsLoaded, persistWhitelist: persistWhitelist, resetRemoveConfirms: resetRemoveConfirms })] })) }));
};
const DangerZone = ({ onBack }) => {
    const [status, setStatus] = SP_REACT.useState("");
    const [disabledDefaults, setDisabledDefaults] = SP_REACT.useState([]);
    const [customNames, setCustomNames] = SP_REACT.useState([]);
    const [settingsLoaded, setSettingsLoaded] = SP_REACT.useState(false);
    const [nonSteamApps, setNonSteamApps] = SP_REACT.useState([]);
    const [busy, setBusy] = SP_REACT.useState(false);
    const [removalProgress, setRemovalProgress] = SP_REACT.useState(null);
    const runRemoval = async (work) => {
        setBusy(true);
        try {
            await work((removed, total) => setRemovalProgress({ removed, total }));
        }
        finally {
            setBusy(false);
            setRemovalProgress(null);
        }
    };
    const activeDefaults = SP_REACT.useMemo(() => DEFAULT_WHITELIST_PATTERNS.filter((p) => !disabledDefaults.includes(p)), [disabledDefaults]);
    const whitelistedIds = SP_REACT.useMemo(() => {
        const set = new Set();
        for (const app of nonSteamApps) {
            const lower = app.name.toLowerCase();
            const matchesDefault = activeDefaults.some((p) => lower.includes(p));
            if (matchesDefault || customNames.includes(app.name)) {
                set.add(app.appId);
            }
        }
        return set;
    }, [nonSteamApps, activeDefaults, customNames]);
    const loadNonSteamApps = () => {
        const apps = [];
        try {
            if (typeof collectionStore === "undefined") {
                logWarn("collectionStore not available");
                setNonSteamApps([]);
                return;
            }
            const deckApps = collectionStore.deckDesktopApps?.apps;
            if (!deckApps) {
                logWarn("deckDesktopApps.apps not available");
                setNonSteamApps([]);
                return;
            }
            logInfo(`deckDesktopApps.apps size: ${deckApps.size}`);
            const appIds = Array.from(deckApps.keys());
            for (const appId of appIds) {
                let name = `Unknown (${appId})`;
                if (typeof appStore !== "undefined") {
                    const overview = appStore.GetAppOverviewByAppID(appId);
                    if (overview) {
                        name = overview.strDisplayName || overview.display_name || name;
                    }
                }
                apps.push({ appId, name });
            }
        }
        catch (e) {
            logError(`Failed to enumerate non-steam games: ${e}`);
        }
        apps.sort((a, b) => a.name.localeCompare(b.name));
        setNonSteamApps(apps);
    };
    SP_REACT.useEffect(() => {
        mountPruneLeaseOwner(DANGER_ZONE_LEASE_OWNER);
        loadNonSteamApps();
        getWhitelistSettings()
            .then((s) => {
            setDisabledDefaults(s.disabled_defaults);
            setCustomNames(s.custom_names);
            setSettingsLoaded(true);
        })
            .catch((e) => logError(`Failed to load whitelist settings: ${e}`));
        return () => {
            detach(releasePruneLeasesByOwner(DANGER_ZONE_LEASE_OWNER));
        };
    }, []);
    const persistWhitelist = (newDisabled, newCustom) => {
        setDisabledDefaults(newDisabled);
        setCustomNames(newCustom);
        updateWhitelistSettings(newDisabled, newCustom).catch((e) => logError(`Failed to update whitelist settings: ${e}`));
    };
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSection, { children: SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: onBack, onFocus: scrollToTop, children: "Back" }) }) }), busy && (SP_JSX.jsx(DFL.PanelSection, { children: SP_JSX.jsx(LoadingRow, { label: removalProgress ? `Removing ${removalProgress.removed} of ${removalProgress.total}...` : "Removing..." }) })), SP_JSX.jsx(RemovedGamesCleanupSection, {}), SP_JSX.jsx(ShortcutRemovalSection, { loadNonSteamApps: loadNonSteamApps, status: status, setStatus: setStatus, busy: busy, runRemoval: runRemoval }), SP_JSX.jsx(OrphanedGridCleanupSection, {}), SP_JSX.jsx(RetroDeckSection, { nonSteamApps: nonSteamApps, whitelistedIds: whitelistedIds, disabledDefaults: disabledDefaults, customNames: customNames, settingsLoaded: settingsLoaded, persistWhitelist: persistWhitelist, loadNonSteamApps: loadNonSteamApps, setStatus: setStatus, busy: busy, runRemoval: runRemoval })] }));
};

function formatFinishedDescription(item) {
    if (item.status === "completed")
        return `Completed — ${formatBytes$1(item.total_bytes)}`;
    if (item.status === "failed") {
        const detail = item.error ? `: ${item.error}` : "";
        return `Failed${detail}`;
    }
    return "Cancelled";
}
const DownloadQueue = ({ onBack }) => {
    const downloads = useDownloads();
    SP_REACT.useEffect(() => {
        detach(getDownloadQueue().then((result) => {
            setDownloads(result.downloads);
        }));
    }, []);
    const handleCancel = async (romId) => {
        try {
            const result = await cancelDownload(romId);
            if (!result.success) {
                showToast(result.message || "Could not cancel the download");
            }
        }
        catch {
            showToast("Could not cancel the download");
        }
    };
    const handlePause = async (romId) => {
        try {
            await pauseDownload(romId);
        }
        catch {
        }
    };
    const handleResume = async (romId) => {
        try {
            await resumeDownload(romId);
        }
        catch {
        }
    };
    const handleClearCompleted = async () => {
        try {
            await clearCompletedDownloads();
        }
        catch {
            return;
        }
        removeTerminalDownloads();
    };
    const active = downloads.filter((d) => d.status === "queued" || d.status === "downloading" || d.status === "paused" || d.status === "extracting");
    const finished = downloads.filter((d) => d.status === "completed" || d.status === "failed" || d.status === "cancelled");
    const hasFinished = finished.length > 0;
    return (SP_JSX.jsxs(SP_JSX.Fragment, { children: [SP_JSX.jsx(DFL.PanelSection, { children: SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: onBack, onFocus: scrollToTop, children: "Back" }) }) }), SP_JSX.jsx(DFL.PanelSection, { title: "Downloads", children: downloads.length === 0 ? (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: "No downloads" }) })) : (SP_JSX.jsxs(SP_JSX.Fragment, { children: [active.map((item) => (SP_JSX.jsx(DownloadProgressRow, { caption: SP_JSX.jsxs(SP_JSX.Fragment, { children: [item.rom_name, " (", item.platform_name, ")", item.status === "paused" ? " — Paused" : "", item.status === "extracting" ? " — Extracting…" : ""] }), bytesDownloaded: item.bytes_downloaded, totalBytes: item.total_bytes }, item.rom_id))), active.map((item) => item.status === "extracting" ? null : (SP_JSX.jsxs(SP_REACT.Fragment, { children: [item.status === "downloading" && item.resumable && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs(DFL.ButtonItem, { layout: "below", onClick: () => {
                                            detach(handlePause(item.rom_id));
                                        }, children: ["Pause ", item.rom_name] }) })), item.status === "paused" && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs(DFL.ButtonItem, { layout: "below", onClick: () => {
                                            detach(handleResume(item.rom_id));
                                        }, children: ["Resume ", item.rom_name] }) })), SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsxs(DFL.ButtonItem, { layout: "below", onClick: () => {
                                            detach(handleCancel(item.rom_id));
                                        }, children: ["Cancel ", item.rom_name] }) })] }, `actions-${item.rom_id}`))), finished.map((item) => (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.Field, { label: item.rom_name, description: formatFinishedDescription(item) }) }, item.rom_id))), hasFinished && (SP_JSX.jsx(DFL.PanelSectionRow, { children: SP_JSX.jsx(DFL.ButtonItem, { layout: "below", onClick: () => {
                                    detach(handleClearCompleted());
                                }, children: "Clear Completed" }) }))] })) })] }));
};

let gameActionHook = null;
const MIGRATION_TOAST_BODY = "Pending RetroDECK migration. Open the plugin QAM to migrate or dismiss.";
async function ensureTrackingConfiguredWatcher(romId) {
    const trackingResult = await isSaveTrackingConfigured(romId).catch((e) => {
        logError(`Watcher tracking check failed (assuming configured): ${e}`);
        return { configured: true };
    });
    if (trackingResult.configured)
        return;
    let setupInfo;
    try {
        setupInfo = await getSaveSetupInfo(romId);
    }
    catch (e) {
        logError(`Watcher save-setup fetch failed (proceeding unconfigured): ${e}`);
        return;
    }
    await applyLaunchGateSetupOutcome(resolveSaveSetupOutcome(setupInfo), {
        rid: romId,
        confirmSlotChoice,
        toast: () => undefined,
        dispatchSavesTab: () => undefined,
    }).catch((e) => logError(`Watcher auto-adopt slot failed (proceeding): ${e}`));
}
async function checkCoreChangeWatcher(romId, prompts) {
    const coreCheck = await checkCoreChange(romId).catch((e) => {
        logError(`Watcher core-change check failed (assuming unchanged): ${e}`);
        return { changed: false };
    });
    if (!coreCheck.changed)
        return true;
    return prompts.confirmCoreChange(coreCheck.old_label ?? coreCheck.old_core ?? "Unknown", coreCheck.new_label ?? coreCheck.new_core ?? "Unknown");
}
const PRE_LAUNCH_SYNC_TIMEOUT_MS = 15000;
async function preLaunchSyncWatcher(romId) {
    let result;
    try {
        result = await Promise.race([
            preLaunchSync(romId),
            new Promise((_, reject) => setTimeout(() => reject(new Error("timeout")), PRE_LAUNCH_SYNC_TIMEOUT_MS)),
        ]);
    }
    catch (e) {
        logError(`Watcher pre-launch sync failed (surfacing fallback confirm): ${e}`);
        return { success: false, message: "Couldn't sync saves with RomM server." };
    }
    if (result.reason !== undefined && BENIGN_SYNC_SKIP_REASONS.includes(result.reason)) {
        return { success: true, message: result.message };
    }
    const outcome = { success: result.success, message: result.message };
    if (result.conflicts)
        outcome.conflicts = result.conflicts;
    return outcome;
}
function makeWatcherOps(romId, prompts) {
    return {
        migrationPending: () => getMigrationState().pending,
        hasLaunchTarget: () => romHasLaunchTarget(romId, "Watcher"),
        ensureTrackingConfigured: async () => {
            await ensureTrackingConfiguredWatcher(romId);
            return "proceed";
        },
        checkCoreChange: () => checkCoreChangeWatcher(romId, prompts),
        checkReachability: async () => {
            try {
                const { online } = await probeReachability();
                reportServerReachable(online);
                return online;
            }
            catch (e) {
                logError(`Watcher reachability probe failed (treating as offline): ${e}`);
                return false;
            }
        },
        preLaunchSync: () => preLaunchSyncWatcher(romId),
        checkLocalDrift: async () => (await checkLocalDrift(romId).catch((e) => {
            logError(`Watcher local-drift check failed (treating as not-drifted): ${e}`);
            return { drifted: false };
        })).drifted,
    };
}
function bareRelaunch(appId) {
    markLaunchSkipped(appId);
    const gameId = appStore.GetAppOverviewByAppID(appId)?.GetGameID?.() ?? String(appId);
    SteamClient.Apps.RunGame(gameId, "", -1, 100);
}
async function relaunch(appId, romId, admission) {
    const reconfirm = await reconfirmLaunchOptions(romId, appId, "Watcher", admission);
    if (reconfirm.status === "cancelled")
        return;
    if (reconfirm.status === "timeout") {
        showToast("Launch cancelled — try again");
        return;
    }
    bareRelaunch(appId);
}
async function handleWatcherVerdict(verdict, appId, romId, admission, prompts) {
    switch (verdict.decision) {
        case "allow":
            await relaunch(appId, romId, admission);
            return "done";
        case "abort":
            return "done";
        case "block":
            if (verdict.reason === "migration_pending") {
                showToast(MIGRATION_TOAST_BODY);
            }
            else if (verdict.reason === "no_launch_target") {
                showToast(NO_LAUNCH_TARGET_TOAST_BODY);
            }
            return "done";
        case "conflict": {
            const resolution = await prompts.resolveConflicts(verdict.conflicts);
            if (resolution === "cancel")
                return "done";
            globalThis.dispatchEvent(new CustomEvent("romm_data_changed", { detail: { type: "save_sync", rom_id: romId } }));
            await relaunch(appId, romId, admission);
            return "done";
        }
        case "offline_drift": {
            const choice = await prompts.askOfflineDrift();
            if (choice === "start_anyway")
                await relaunch(appId, romId, admission);
            if (choice === "retry")
                return "retry";
            return "done";
        }
        case "sync_failed": {
            const proceed = await prompts.confirmFallbackLaunch(verdict.message);
            if (proceed)
                await relaunch(appId, romId, admission);
            return "done";
        }
    }
}
async function runWatcherGate(appId, romId, admission, prompts) {
    let verdict = await runLaunchGate(appId, romId, makeWatcherOps(romId, prompts)).catch((e) => {
        logError(`Watcher gate threw (failing open to allow): ${e}`);
        return { decision: "allow" };
    });
    while ((await handleWatcherVerdict(verdict, appId, romId, admission, prompts)) === "retry") {
        verdict = await runLaunchGate(appId, romId, makeWatcherOps(romId, prompts)).catch((e) => {
            logError(`Watcher gate threw (failing open to allow): ${e}`);
            return { decision: "allow" };
        });
    }
}
async function isRomInstalled(appId, romId) {
    try {
        return (await getInstalledRom(romId)) != null;
    }
    catch (e) {
        logError(`Watcher installed check threw (falling back to cached install flag): ${e}`);
        const cached = await getCachedGameDetail(appId).catch((cacheErr) => {
            logError(`Watcher cached-detail fallback failed (treating as not installed): ${cacheErr}`);
            return null;
        });
        return cached?.installed === true;
    }
}
function registerLaunchInterceptor(prompts) {
    gameActionHook = SteamClient.Apps.RegisterForGameActionStart((gameActionId, appIdStr, action, _launchSource) => {
        if (action !== "LaunchApp")
            return;
        const appId = Number.parseInt(appIdStr, 10);
        if (Number.isNaN(appId) || !isRomMAppId(appId))
            return;
        if (consumeLaunchSkip(appId))
            return;
        const pressedRomId = getAppIdRomIdMapSnapshot()[String(appId)];
        if ((pressedRomId !== undefined && isSessionActive(pressedRomId)) || isAppRunning(appId)) {
            logInfo(`Launch interceptor: appId=${appId} already running — skipping pre-launch sync`);
            return;
        }
        SteamClient.Apps.CancelGameAction(gameActionId);
        const admission = capturePruneLeaseAdmission();
        detach((async () => {
            try {
                refreshMigrationState()
                    .then(({ retrodeck, save_sort }) => {
                    setMigrationStatus(retrodeck);
                    setSaveSortMigrationStatus(save_sort);
                })
                    .catch((e) => logError(`Pre-launch migration refresh failed: ${e}`));
                const romId = getAppIdRomIdMapSnapshot()[String(appId)];
                if (romId == null) {
                    if (!isPruneLeaseAdmissionCurrent(admission))
                        return;
                    bareRelaunch(appId);
                    return;
                }
                if (!(await isRomInstalled(appId, romId))) {
                    if (!isPruneLeaseAdmissionCurrent(admission))
                        return;
                    showToast("ROM not downloaded. Open the plugin to download it first.");
                    return;
                }
                await runWatcherGate(appId, romId, admission, prompts);
            }
            catch (e) {
                logError(`Launch interceptor error: ${e}`);
                if (!isPruneLeaseAdmissionCurrent(admission))
                    return;
                bareRelaunch(appId);
            }
        })());
    });
    logInfo("Launch interceptor registered");
}
function unregisterLaunchInterceptor() {
    if (gameActionHook) {
        gameActionHook.unregister();
        gameActionHook = null;
    }
    logInfo("Launch interceptor unregistered");
}

async function relocateShortcutsToLauncher() {
    const plan = await getShortcutRelocation();
    if (plan.status === "done")
        return { status: "relocated" };
    if (plan.status === "blocked") {
        logInfo(`launcher relocation: nothing rewritten — ${plan.message}`);
        return { status: "blocked" };
    }
    try {
        for (const appId of plan.app_ids) {
            SteamClient.Apps.SetShortcutExe(appId, plan.exe);
            SteamClient.Apps.SetShortcutStartDir(appId, plan.start_dir);
        }
    }
    catch (e) {
        logError(`launcher relocation: stopped after a failed write, leaving the rest for the next start: ${e}`);
        return { status: "blocked" };
    }
    logInfo(`launcher relocation: pointed ${plan.app_ids.length} shortcut(s) at ${plan.exe}`);
    return { status: "relocated" };
}

async function fetchMetadataCachePages(pageSize, timeoutMs) {
    const cache = {};
    let collected = 0;
    let total = Number.POSITIVE_INFINITY;
    let offset = 0;
    while (collected < total) {
        const page = await withTimeout(getMetadataCachePage(offset, pageSize), timeoutMs);
        total = page.total;
        const keys = Object.keys(page.items);
        if (keys.length === 0)
            break;
        for (const key of keys)
            cache[key] = page.items[key];
        collected += keys.length;
        offset += pageSize;
    }
    return cache;
}

const SNAPSHOT_BUDGET_BYTES = 56 * 1024;
const REPORT_ATTEMPTS = 3;
const REPORT_TIMEOUT_MS = 5000;
const handledTokens = new Set();
let actionQueue = Promise.resolve();
let actionGeneration = 0;
function asciiJsonSize(value) {
    let bytes = 0;
    for (const char of JSON.stringify(value)) {
        const codePoint = char.codePointAt(0) ?? 0;
        if (codePoint <= 0x7f)
            bytes += 1;
        else if (codePoint <= 0xffff)
            bytes += 6;
        else
            bytes += 12;
    }
    return bytes;
}
function isPruneAction(value) {
    if (!value || typeof value !== "object")
        return false;
    const item = value;
    if (typeof item.run_id !== "string" || typeof item.action_token !== "string" || typeof item.app_id !== "number") {
        return false;
    }
    if (item.action === "capture_shortcut_snapshot")
        return true;
    if (item.action === "remove_shortcut") {
        return (item.expected_snapshot === undefined ||
            (item.expected_snapshot !== null && typeof item.expected_snapshot === "object"));
    }
    return (item.action === "repoint_shortcut" &&
        typeof item.target_rom_id === "number" &&
        typeof item.launch_options === "string" &&
        typeof item.target_installed === "boolean");
}
function requireString(value, field) {
    if (typeof value !== "string")
        throw new Error(`Steam shortcut ${field} was unavailable`);
    return value;
}
async function captureShortcutSnapshot(appId) {
    if (typeof collectionStore === "undefined" || typeof appStore === "undefined") {
        throw new TypeError("Steam shortcut, collection, or playtime state was unavailable");
    }
    const liveApps = collectionStore.deckDesktopApps?.apps;
    if (!liveApps)
        throw new Error("Steam shortcut store was unavailable");
    if (!liveApps.has(appId))
        throw new Error("Steam shortcut is absent");
    const details = await getAppDetails(appId);
    if (!isRomMShortcutDetails(details))
        throw new Error("The live shortcut is not owned by Arcoon Deck");
    const overview = appStore.GetAppOverviewByAppID(appId);
    if (!overview)
        throw new Error("Steam shortcut playtime state was unavailable");
    const collections = collectionStore.userCollections
        .filter((collection) => collection.apps.has(appId))
        .map((collection) => ({
        id: requireString(collection.id, "collection id"),
        name: requireString(collection.displayName, "collection name"),
    }))
        .sort((left, right) => left.id.localeCompare(right.id));
    const snapshot = {
        app_id: appId,
        name: requireString(details.strDisplayName ?? overview.strDisplayName, "name"),
        exe: requireString(details.strShortcutExe, "executable"),
        start_dir: requireString(details.strShortcutStartDir, "start directory"),
        launch_options: requireString(details.strLaunchOptions ?? details.LaunchOptions, "launch options"),
        minutes_playtime_forever: overview.minutes_playtime_forever ?? null,
        minutes_playtime_last_two_weeks: overview.minutes_playtime_last_two_weeks ?? null,
        last_played: overview.rt_last_time_played ?? null,
        collections,
    };
    if (asciiJsonSize(snapshot) > SNAPSHOT_BUDGET_BYTES) {
        throw new Error("Complete Steam shortcut state is too large for a safe recovery snapshot");
    }
    return snapshot;
}
async function reportWithRetry(request) {
    let lastMessage = "Action report was rejected.";
    for (let attempt = 1; attempt <= REPORT_ATTEMPTS; attempt++) {
        try {
            const result = await withTimeout(reportPruneAction(request), REPORT_TIMEOUT_MS);
            if (result.success)
                return true;
            lastMessage = result.message;
            if (result.reason === "stale_action" || result.reason === "local_state_changed")
                break;
        }
        catch (e) {
            lastMessage = e instanceof Error ? e.message : String(e);
        }
        if (attempt < REPORT_ATTEMPTS) {
            await new Promise((resolve) => setTimeout(resolve, attempt * 100));
        }
    }
    logError(`Failed to report prune action ${request.action_token}: ${lastMessage}`);
    return false;
}
function claimAction(action) {
    return reportWithRetry({
        phase: "claim",
        run_id: action.run_id,
        action_token: action.action_token,
        action: action.action,
        app_id: action.app_id,
        target_rom_id: action.action === "repoint_shortcut" ? action.target_rom_id : null,
    });
}
function assertCurrent(generation) {
    if (generation !== actionGeneration)
        throw new Error("Cleanup action was cancelled before Steam mutation");
}
function shortcutAbsentReport(action) {
    return {
        phase: "complete",
        run_id: action.run_id,
        action_token: action.action_token,
        success: true,
        message: "Steam confirmed the shortcut is already absent.",
        shortcut_absent: true,
    };
}
async function captureSnapshotReport(action) {
    try {
        return {
            phase: "complete",
            run_id: action.run_id,
            action_token: action.action_token,
            success: true,
            message: "Steam shortcut state captured.",
            snapshot: await captureShortcutSnapshot(action.app_id),
        };
    }
    catch (error) {
        if (error instanceof Error && error.message === "Steam shortcut is absent")
            return shortcutAbsentReport(action);
        throw error;
    }
}
async function repointShortcutReport(action, generation, attempt) {
    const details = await getAppDetails(action.app_id);
    if (!isRomMShortcutDetails(details))
        throw new Error("The live shortcut is not owned by Arcoon Deck");
    assertCurrent(generation);
    const result = {
        app_id: action.app_id,
        launch_options: action.launch_options,
    };
    attempt.issued = true;
    if (!(await setLaunchOptionsConfirmed(result.app_id, result.launch_options))) {
        throw new Error("Steam did not confirm the target launch command");
    }
    return {
        phase: "complete",
        run_id: action.run_id,
        action_token: action.action_token,
        success: true,
        message: "Shortcut repointed and launch command confirmed.",
    };
}
async function removeShortcutReport(action, generation, attempt) {
    let fresh;
    try {
        fresh = await captureShortcutSnapshot(action.app_id);
    }
    catch (error) {
        if (error instanceof Error && error.message === "Steam shortcut is absent")
            return shortcutAbsentReport(action);
        throw error;
    }
    if (action.expected_snapshot && JSON.stringify(fresh) !== JSON.stringify(action.expected_snapshot)) {
        throw new Error("Steam shortcut state changed after recovery was sealed");
    }
    assertCurrent(generation);
    const removal = await removeShortcutConfirmedOutcome(action.app_id, 3000, true);
    attempt.issued = removal.status === "attempted_unconfirmed" || removal.status === "confirmed";
    if (removal.status !== "confirmed") {
        throw new Error("Steam did not confirm owned-shortcut removal");
    }
    return {
        phase: "complete",
        run_id: action.run_id,
        action_token: action.action_token,
        success: true,
        message: "Steam confirmed shortcut removal.",
    };
}
async function executePruneAction(action, generation) {
    let claimed = false;
    const attempt = { issued: false };
    const claim = async () => {
        if (claimed)
            return true;
        claimed = await claimAction(action);
        return claimed;
    };
    let report;
    try {
        assertCurrent(generation);
        if (!(await claim()))
            return;
        assertCurrent(generation);
        if (action.action === "capture_shortcut_snapshot") {
            report = await captureSnapshotReport(action);
        }
        else if (action.action === "repoint_shortcut") {
            report = await repointShortcutReport(action, generation, attempt);
        }
        else {
            report = await removeShortcutReport(action, generation, attempt);
        }
    }
    catch (e) {
        report = {
            phase: "complete",
            run_id: action.run_id,
            action_token: action.action_token,
            success: false,
            reason: "steam_action_failed",
            message: e instanceof Error ? e.message : String(e),
            ...(attempt.issued ? { mutation_attempted: true } : {}),
        };
    }
    if (!(await claim()))
        return;
    await reportWithRetry(report);
}
function handlePruneAction(value) {
    if (!isPruneAction(value)) {
        logError("Ignored an invalid prune action event.");
        return Promise.resolve();
    }
    if (handledTokens.has(value.action_token))
        return Promise.resolve();
    handledTokens.add(value.action_token);
    const generation = actionGeneration;
    const queued = actionQueue.then(() => executePruneAction(value, generation));
    actionQueue = queued.catch(() => { });
    return queued;
}
function cancelPruneActions() {
    actionGeneration++;
    handledTokens.clear();
    actionQueue = Promise.resolve();
}

let currentPage = "main";
let currentSection = null;
const QAMPanel = () => {
    const [page, setPageState] = SP_REACT.useState(currentPage);
    const [settingsSection, setSettingsSectionState] = SP_REACT.useState(currentSection);
    const rootRef = SP_REACT.useRef(null);
    const setPage = (p, section = null) => {
        currentPage = p;
        currentSection = section;
        setPageState(p);
        setSettingsSectionState(section);
    };
    const navigate = (target) => {
        if (typeof target === "string")
            setPage(target);
        else
            setPage(target.page, target.section);
    };
    SP_REACT.useEffect(() => {
        const el = rootRef.current;
        if (!el)
            return;
        const container = findOutermostScrollParent(el);
        const rafHandle = requestAnimationFrame(() => {
            if (container)
                container.scrollTop = 0;
        });
        const ownsFocus = el.querySelector(`[${OWNS_ENTRY_FOCUS_ATTR}]`) !== null;
        const focusTimer = ownsFocus
            ? undefined
            : setTimeout(() => placeEntryFocus(el, pageEntryStop), ENTRY_FOCUS_DELAY_MS);
        return () => {
            cancelAnimationFrame(rafHandle);
            clearTimeout(focusTimer);
        };
    }, [page]);
    let content;
    switch (page) {
        case "sync":
            content = SP_JSX.jsx(SyncPage, { onBack: () => setPage("main") });
            break;
        case "settings":
            content = (SP_JSX.jsx(SettingsPage, { onBack: () => setPage("main"), ...(settingsSection === null ? {} : { section: settingsSection }) }));
            break;
        case "library":
            content = SP_JSX.jsx(LibraryPage, { onBack: () => setPage("main") });
            break;
        case "data":
            content = SP_JSX.jsx(DangerZone, { onBack: () => setPage("main") });
            break;
        case "downloads":
            content = SP_JSX.jsx(DownloadQueue, { onBack: () => setPage("main") });
            break;
        default:
            content = SP_JSX.jsx(MainPage, { onNavigate: navigate });
    }
    return (SP_JSX.jsx("div", { ref: rootRef, children: page === "main" ? content : SP_JSX.jsx(DFL.Focusable, { onCancelButton: () => setPage("main"), children: content }) }));
};
function buildSyncCompleteToast(data, delta) {
    const parts = [];
    if (delta.added > 0)
        parts.push(`${delta.added} added`);
    if (delta.removed > 0)
        parts.push(`${delta.removed} removed`);
    const summary = parts.join(", ");
    if (data.interrupt_reason) {
        const body = summary ? `${data.interrupt_reason.replace(/\.$/, "")} (${summary} so far).` : data.interrupt_reason;
        return { body, duration: 15000 };
    }
    if (data.interrupted) {
        return { body: summary ? `Sync interrupted — ${summary} so far.` : "Sync interrupted." };
    }
    if (data.cancelled) {
        return { body: summary ? `Sync cancelled — ${summary} so far.` : "Sync cancelled." };
    }
    let body = summary ? `Sync complete — ${summary}.` : "Library up to date.";
    if (data.restart_recommended) {
        body += " Steam restart recommended before further large operations.";
    }
    return { body };
}
const ROMM_COLLECTION_NAME = /^RomM: \[([^\]]+)\]/;
const COLLECTION_HOST_SUFFIX = /\s\([^)]+\)$/;
function platformOfCollection(displayName) {
    return displayName.slice(6).replace(COLLECTION_HOST_SUFFIX, "");
}
function isStalePlatformCollection(displayName, suffix, activePlatforms) {
    if (!displayName.startsWith("RomM: ") || displayName.slice(6).startsWith("["))
        return false;
    if (!displayName.endsWith(suffix))
        return false;
    return !activePlatforms.has(platformOfCollection(displayName).toLowerCase());
}
function isStaleRomMCollection(displayName, suffix, activeNames) {
    if (!displayName.startsWith("RomM: [") || !displayName.endsWith(suffix))
        return false;
    const match = ROMM_COLLECTION_NAME.exec(displayName);
    return match ? !activeNames.has(match[1].toLowerCase()) : false;
}
async function removeStaleCollections(activePlatformNames, activeCollectionNames, signal) {
    const hostname = await getHostname();
    if (isPruneLeaseCancelled(signal))
        return;
    const suffix = ` (${hostname})`;
    const activePlatforms = new Set(activePlatformNames.map((name) => name.toLowerCase()));
    for (const collection of collectionStore.userCollections.filter((candidate) => isStalePlatformCollection(candidate.displayName, suffix, activePlatforms))) {
        const platformName = platformOfCollection(collection.displayName);
        logInfo(`Removing stale platform collection "${collection.displayName}"`);
        await clearPlatformCollection(platformName, signal);
        if (isPruneLeaseCancelled(signal))
            return;
    }
    const activeNames = new Set(activeCollectionNames.map((name) => name.toLowerCase()));
    for (const collection of collectionStore.userCollections.filter((candidate) => isStaleRomMCollection(candidate.displayName, suffix, activeNames))) {
        logInfo(`Removing stale RomM collection "${collection.displayName}"`);
        if (isPruneLeaseCancelled(signal))
            return;
        await collection.Delete();
    }
}
async function publishSwitchesUntilCancelled(pending, signal) {
    for (const item of pending) {
        if (isPruneLeaseCancelled(signal))
            return;
        await publishCommittedVersionSwitch(item.appId, item.romId, undefined, signal);
    }
}
function shortcutActionLabel(committedAction) {
    return committedAction === "remove_shortcut" ? "Shortcut removal" : "Shortcut repoint";
}
function buildPruneCompleteToast(completed) {
    const ambiguousPartial = completed.results.find((item) => item.status === "partial" && item.action_ambiguous);
    const committedPartial = completed.results.find((item) => item.status === "partial" && item.committed_action);
    const subtext = ambiguousPartial?.message ?? committedPartial?.message ?? completed.message;
    if (ambiguousPartial) {
        const label = shortcutActionLabel(ambiguousPartial.committed_action);
        return { body: `${label} outcome is uncertain; source data was retained.`, subtext };
    }
    if (committedPartial) {
        const label = shortcutActionLabel(committedPartial.committed_action);
        return { body: `${label} committed; local cleanup incomplete.`, subtext };
    }
    const removed = completed.removed_count ?? completed.removed_rom_ids.length;
    if (!removed)
        return { body: completed.message || "No removed RomM games were cleaned up.", subtext };
    const skipped = completed.problem_count ??
        completed.results.filter((item) => ["failed", "skipped", "partial"].includes(item.status)).length;
    const skippedNote = skipped ? `; ${skipped} group(s) skipped` : "";
    const plural = removed === 1 ? "y" : "ies";
    return { body: `Removed ${removed} local entr${plural}${skippedNote}.`, subtext };
}
function registerAppIds(map) {
    for (const appIds of Object.values(map)) {
        for (const appId of appIds) {
            registerRomMAppId(appId);
        }
    }
}
var index = definePlugin(() => {
    mountPruneLeasePlugin();
    const pluginAdmission = capturePruneLeaseAdmission();
    registerGameDetailPatch();
    registerLaunchInterceptor({
        confirmCoreChange: showCoreChangeModal,
        resolveConflicts: handleConflicts,
        askOfflineDrift: showOfflineDriftModal,
        confirmFallbackLaunch: showFallbackLaunchModal,
    });
    const RETRY_DELAYS = [2000, 5000, 10000, 15000, 20000];
    const CALLABLE_TIMEOUT = 5000;
    const METADATA_PAGE_SIZE = 500;
    let initAttempt = 0;
    let initDone = false;
    let syncContinuationController = new AbortController();
    let staleRemovalTail = Promise.resolve();
    async function loadAppIdsAndMetadata() {
        const appIdMap = await withTimeout(getAppIdRomIdMap(), CALLABLE_TIMEOUT);
        const cache = await fetchMetadataCachePages(METADATA_PAGE_SIZE, CALLABLE_TIMEOUT);
        registerMetadataPatches(cache, appIdMap);
        for (const appIdStr of Object.keys(appIdMap)) {
            const appId = Number.parseInt(appIdStr, 10);
            if (!Number.isNaN(appId)) {
                registerRomMAppId(appId);
            }
        }
        detach(applyAllMetadata());
        try {
            const { playtime } = await withTimeout(getAllPlaytime(), CALLABLE_TIMEOUT);
            await applyAllPlaytime(playtime, appIdMap);
        }
        catch (e) {
            console.warn("[RomM] Failed to apply playtime:", e);
        }
        initDone = true;
        const attempts = initAttempt + 1;
        if (attempts > 1) {
            logInfo(`App ID init succeeded after ${attempts} attempts (backend was slow to start)`);
        }
        else {
            logInfo(`App ID init succeeded (attempt 1)`);
        }
    }
    detach((async () => {
        while (!initDone && initAttempt < RETRY_DELAYS.length + 1) {
            try {
                await loadAppIdsAndMetadata();
            }
            catch {
                if (initAttempt < RETRY_DELAYS.length) {
                    await new Promise((r) => setTimeout(r, RETRY_DELAYS[initAttempt]));
                }
                initAttempt++;
            }
        }
        if (initDone) {
            try {
                const result = await getInstalledRelaunchOptions();
                if (result.success) {
                    await withPruneLease(result.prune_lease_token, "Startup reconcile", (signal) => batchConfirmLaunchOptions(result.items, "startup_reconcile", signal), "Startup reconcile", pluginAdmission);
                }
            }
            catch (e) {
                logError(`startup_reconcile: failed to reconcile launch options: ${e}`);
            }
        }
    })());
    detach((async () => {
        try {
            const result = await withTimeout(testConnection(), CALLABLE_TIMEOUT);
            if (result.reason === "version_error") {
                setVersionError(result.message);
            }
            else if (result.success) {
                setVersionError(null);
            }
        }
        catch {
        }
    })());
    detach((async () => {
        try {
            const status = await getMigrationStatus();
            if (status.pending) {
                setMigrationStatus(status);
            }
        }
        catch (e) {
            logError(`Failed to check migration status: ${e}`);
        }
    })());
    detach((async () => {
        try {
            const status = await getSaveSortMigrationStatus();
            if (status.pending) {
                setSaveSortMigrationStatus(status);
                showToast("RetroArch save sorting changed. Go to Settings to migrate save files.");
            }
        }
        catch (e) {
            logError(`Failed to check save sort migration status: ${e}`);
        }
    })());
    detach((async () => {
        try {
            await fetchSettingsResetState();
        }
        catch (e) {
            logError(`Failed to check settings reset notice: ${e}`);
        }
    })());
    detach((async () => {
        try {
            const relocation = await relocateShortcutsToLauncher();
            setLauncherRelocated(relocation.status === "relocated");
        }
        catch (e) {
            logError(`Failed to point the shortcuts at the launcher: ${e}`);
        }
    })());
    detach((async () => {
        try {
            await syncEmulatorShortcuts();
        }
        catch (e) {
            logError(`Failed to refresh the emulator collection: ${e}`);
        }
    })());
    detach((async () => {
        try {
            await fetchLegacyInstallState();
        }
        catch (e) {
            logError(`Failed to check for a legacy install: ${e}`);
        }
    })());
    detach((async () => {
        try {
            await fetchDataLocationState();
        }
        catch (e) {
            logError(`Failed to read the data location notice: ${e}`);
        }
    })());
    detach((async () => {
        try {
            const syncSettings = await getSaveSyncSettings();
            if (syncSettings.save_sync_enabled) {
                await ensureDeviceRegistered();
            }
            await initSessionManager();
        }
        catch (e) {
            logError(`Failed to init save sync: ${e}`);
        }
    })());
    const onSyncComplete = (data) => {
        const syncAdmission = capturePruneLeaseAdmission();
        logInfo(`sync_complete received: ${data.total_games} games, cancelled=${data.cancelled ?? false}`);
        const { body, duration } = buildSyncCompleteToast(data, getSyncDelta());
        showToast(body, duration !== undefined ? { duration } : undefined);
        updateSyncProgress({ running: false, stage: data.cancelled ? "cancelled" : "done" });
        resetSyncDelta();
        registerAppIds(data.platform_app_ids);
        registerAppIds(data.romm_collection_app_ids ?? {});
        const reconcileLaunchOptions = async (signal) => {
            try {
                const result = await getInstalledRelaunchOptions();
                if (result.success) {
                    await withPruneLease(result.prune_lease_token, "Installed reconcile", (innerSignal) => {
                        if (isPruneLeaseCancelled(innerSignal))
                            return Promise.resolve();
                        return batchConfirmLaunchOptions(result.items, "sync_reconcile", signal);
                    }, "Installed reconcile", syncAdmission);
                }
            }
            catch (e) {
                logError(`sync_reconcile: failed to reconcile launch options: ${e}`);
            }
        };
        const reconcileCollections = async (signal) => {
            try {
                if (Object.keys(data.platform_app_ids).length > 0) {
                    await createOrUpdateCollections(data.platform_app_ids, undefined, signal);
                }
                if (isPruneLeaseCancelled(signal))
                    return;
                if (data.romm_collection_app_ids && Object.keys(data.romm_collection_app_ids).length > 0) {
                    await createOrUpdateRomMCollections(data.romm_collection_app_ids, undefined, signal);
                }
                if (isPruneLeaseCancelled(signal))
                    return;
                if (!data.cancelled && typeof collectionStore !== "undefined") {
                    await removeStaleCollections(Object.keys(data.platform_app_ids), Object.keys(data.romm_collection_app_ids ?? {}), signal);
                }
            }
            catch (e) {
                logError(`Failed to manage RomM collections: ${e}`);
            }
        };
        const reconcilePlaytime = async (signal) => {
            try {
                const [{ playtime }, appIdMap] = await Promise.all([getAllPlaytime(), getAppIdRomIdMap()]);
                if (isPruneLeaseCancelled(signal))
                    return;
                await applyAllPlaytime(playtime, appIdMap, signal);
            }
            catch (e) {
                logError(`Failed to re-apply playtime after sync: ${e}`);
            }
        };
        const reconcileMetadata = async (signal) => {
            try {
                const [cache, appIdMap] = await Promise.all([
                    fetchMetadataCachePages(METADATA_PAGE_SIZE, CALLABLE_TIMEOUT),
                    getAppIdRomIdMap(),
                ]);
                if (isPruneLeaseCancelled(signal))
                    return;
                registerMetadataPatches(cache, appIdMap);
                await applyAllMetadata(signal);
            }
            catch (e) {
                logError(`Failed to re-apply metadata after sync: ${e}`);
            }
        };
        const continuationController = syncContinuationController;
        const staleRemovals = staleRemovalTail;
        detach(withPruneLease(data.prune_lease_token, "Sync completion", async (leaseSignal) => {
            const abort = () => continuationController.abort();
            if (leaseSignal.aborted)
                abort();
            else
                leaseSignal.addEventListener("abort", abort, { once: true });
            try {
                const signal = continuationController.signal;
                await Promise.allSettled([
                    staleRemovals,
                    reconcileLaunchOptions(signal),
                    reconcileCollections(signal),
                    reconcilePlaytime(signal),
                    reconcileMetadata(signal),
                ]);
            }
            finally {
                leaseSignal.removeEventListener("abort", abort);
            }
        }));
    };
    const syncCompleteListener = addEventListener("sync_complete", onSyncComplete);
    const syncApplyUnitListener = initUnitSyncManager();
    const detachRunUnitsMirror = attachRunUnitsMirror();
    const syncPlanListener = addEventListener("sync_plan", (data) => {
        syncContinuationController.abort();
        syncContinuationController = new AbortController();
        resetSyncDelta();
        seedRunUnits(data.units, data.run_id);
        resetSyncCancel();
        if (getSyncProgress().etaSeconds === undefined) {
            updateSyncProgress({ etaSeconds: estimatePlanSeconds(data.units) });
        }
        beginEtaRun(data.run_id, data.units.map((u) => (u.predicted_skip ? 0 : (u.collapsed_count ?? u.rom_count))), data.total_estimated_items ?? data.total_roms);
        logInfo(`sync_plan received: ${data.total_units} units, ${data.total_roms} ROMs total` +
            (data.total_estimated_items !== undefined ? ` (${data.total_estimated_items} estimated items)` : ""));
    });
    const syncStaleListener = addEventListener("sync_stale", (data) => {
        if (!Array.isArray(data.remove) || data.remove.length === 0)
            return;
        const appIds = [];
        for (const { app_id } of data.remove) {
            if (app_id) {
                appIds.push(app_id);
                recordSyncRemoved(app_id);
            }
        }
        const continuationController = syncContinuationController;
        const previousTail = staleRemovalTail;
        staleRemovalTail = withPruneLease(data.prune_lease_token, "Sync stale removal", async (leaseSignal) => {
            const abort = () => continuationController.abort();
            if (leaseSignal.aborted)
                abort();
            else
                leaseSignal.addEventListener("abort", abort, { once: true });
            try {
                await previousTail;
                const signal = continuationController.signal;
                if (isPruneLeaseCancelled(signal))
                    return;
                await removeShortcutsPaced(appIds, undefined, signal);
                if (!isPruneLeaseCancelled(signal))
                    logInfo(`sync_stale: removed ${data.remove.length} stale shortcuts`);
            }
            finally {
                leaseSignal.removeEventListener("abort", abort);
            }
        }).catch((e) => logError(`sync_stale: stale shortcut removal failed: ${e}`));
    });
    const syncCollectionsListener = addEventListener("sync_collections", (data) => {
        logInfo(`sync_collections received: ${Object.keys(data.platform_app_ids).length} platforms`);
    });
    const syncProgressListener = addEventListener("sync_progress", (progress) => {
        const { etaSeconds } = getSyncProgress();
        setSyncProgress(etaSeconds !== undefined ? { ...progress, etaSeconds } : progress);
    });
    const downloadProgressListener = addEventListener("download_progress", (data) => {
        if (data.status === "cancelled") {
            removeDownload(data.rom_id);
            return;
        }
        const prev = getDownloadState().find((d) => d.rom_id === data.rom_id);
        updateDownload({
            rom_id: data.rom_id,
            rom_name: data.rom_name,
            platform_name: data.platform_name,
            file_name: data.file_name,
            status: data.status,
            progress: data.progress,
            bytes_downloaded: data.bytes_downloaded,
            total_bytes: data.total_bytes,
            resumable: data.resumable ?? prev?.resumable ?? false,
        });
    });
    const downloadCompleteListener = addEventListener("download_complete", (data) => {
        const prev = getDownloadState().find((d) => d.rom_id === data.rom_id);
        updateDownload({
            rom_id: data.rom_id,
            rom_name: data.rom_name,
            platform_name: data.platform_name,
            file_name: prev?.file_name ?? "",
            status: "completed",
            progress: 1,
            bytes_downloaded: prev?.bytes_downloaded ?? 0,
            total_bytes: prev?.total_bytes ?? 0,
            resumable: data.resumable ?? prev?.resumable ?? false,
        });
        showToast(`Downloaded ${data.rom_name}`);
        if (data.app_id !== null) {
            const appId = data.app_id;
            detach((async () => {
                try {
                    const ok = await withPruneLease(data.prune_lease_token, "Download completion", async (signal) => {
                        if (isPruneLeaseCancelled(signal))
                            return false;
                        return setLaunchOptionsConfirmed(appId, data.launch_options);
                    });
                    if (!ok) {
                        logError(`download_complete: failed to confirm launch options for rom ${data.rom_id} (appId ${appId})`);
                    }
                }
                catch (e) {
                    logError(`download_complete: failed to set launch options for rom ${data.rom_id}: ${e}`);
                }
            })());
        }
    });
    const downloadFailedListener = addEventListener("download_failed", (data) => handleGlobalDownloadFailure(data, { getDownloadState, updateDownload }, toaster));
    const pathChangedListener = addEventListener("retrodeck_path_changed", (data) => {
        if (data.cleared) {
            setMigrationStatus({ pending: false });
            return;
        }
        getMigrationStatus()
            .then((status) => setMigrationStatus(status))
            .catch((e) => logError(`Failed to refresh migration status: ${e}`));
    });
    const saveSortChangedListener = addEventListener("save_sort_changed", () => {
        showToast("RetroArch save sorting changed. Go to Settings to migrate save files.");
    });
    const saveStatusListener = addEventListener("save_status_updated", (data) => {
        const hasConflict = hasAnySaveConflict(data);
        globalThis.dispatchEvent(new CustomEvent("romm_data_changed", {
            detail: { type: "save_sync", rom_id: data.rom_id, save_status: data, has_conflict: hasConflict },
        }));
    });
    const migrationRelaunchListener = addEventListener("migration_relaunch_options", (data) => {
        detach(withPruneLease(data.prune_lease_token, "RetroDECK migration", (signal) => batchConfirmLaunchOptions(data.items, "migration_relaunch_options", signal)));
    });
    const serverRetryListener = addEventListener("server_retry_progress", (data) => {
        setServerRetryProgress({ attempt: data.attempt, maxAttempts: data.max_attempts });
    });
    const publishPruneSwitches = async (runId, pending, leaseToken) => {
        if (!leaseToken) {
            logError("Cleanup publication was skipped because its continuation lease was missing.");
            return;
        }
        await withPruneLease(leaseToken, "Cleanup repoint publication", async (signal) => {
            let lastMessage = "Cleanup claim release was not confirmed.";
            for (let attempt = 1; attempt <= 3; attempt++) {
                try {
                    const released = await withTimeout(waitForPruneRelease(runId), 6000);
                    if (released.success) {
                        await publishSwitchesUntilCancelled(pending, signal);
                        return;
                    }
                    lastMessage = released.message;
                }
                catch (e) {
                    lastMessage = e instanceof Error ? e.message : String(e);
                }
                if (attempt < 3)
                    await new Promise((resolve) => setTimeout(resolve, attempt * 100));
            }
            logError(`Cleanup publication could not confirm claim release: ${lastMessage}`);
        }, "root", pluginAdmission);
    };
    const pruneActionListener = addEventListener("prune_action_required", (action) => {
        if (!admitPruneFrame(action.preview_id, action.run_id))
            return;
        detach(handlePruneAction(action));
    });
    const pruneProgressListener = addEventListener("prune_progress", (progress) => setPruneProgress(progress));
    const pruneCompleteListener = addEventListener("prune_complete", (result) => {
        const completed = setPruneComplete(result);
        if (!completed)
            return;
        for (const appId of completed.affected_app_ids)
            invalidateCachedGameDetail(appId);
        for (const appId of completed.removed_app_ids ?? [])
            unregisterRomMAppId(appId);
        globalThis.dispatchEvent(new CustomEvent("romm_data_changed", {
            detail: {
                type: "rom_pruned",
                app_ids: completed.affected_app_ids,
                rom_ids: completed.removed_rom_ids,
            },
        }));
        cancelPruneActions();
        const publications = [];
        for (const item of completed.results) {
            if (item.committed_action === "repoint_shortcut" &&
                !item.action_ambiguous &&
                item.app_id !== undefined &&
                item.target_rom_id !== undefined) {
                publications.push({ appId: item.app_id, romId: item.target_rom_id });
            }
        }
        if (publications.length) {
            detach(publishPruneSwitches(completed.run_id, publications, completed.prune_lease_token));
        }
        else if (completed.prune_lease_token) {
            detach(releasePruneLease(completed.prune_lease_token, "Cleanup completion with nothing to publish"));
        }
        const { body, subtext } = buildPruneCompleteToast(completed);
        showToast(body, { subtext });
    });
    return {
        name: PLUGIN_NAME,
        icon: SP_JSX.jsx(FaGamepad, {}),
        content: SP_JSX.jsx(QAMPanel, {}),
        alwaysRender: true,
        onDismount() {
            syncContinuationController.abort();
            destroySessionManager();
            unregisterLaunchInterceptor();
            unregisterGameDetailPatch();
            unregisterMetadataPatches();
            removeEventListener("sync_complete", syncCompleteListener);
            removeEventListener("sync_apply_unit", syncApplyUnitListener);
            removeEventListener("sync_plan", syncPlanListener);
            removeEventListener("sync_stale", syncStaleListener);
            removeEventListener("sync_collections", syncCollectionsListener);
            removeEventListener("sync_progress", syncProgressListener);
            detachRunUnitsMirror();
            removeEventListener("download_progress", downloadProgressListener);
            removeEventListener("download_complete", downloadCompleteListener);
            removeEventListener("download_failed", downloadFailedListener);
            removeEventListener("retrodeck_path_changed", pathChangedListener);
            removeEventListener("save_sort_changed", saveSortChangedListener);
            removeEventListener("save_status_updated", saveStatusListener);
            removeEventListener("migration_relaunch_options", migrationRelaunchListener);
            removeEventListener("server_retry_progress", serverRetryListener);
            removeEventListener("prune_action_required", pruneActionListener);
            cancelPruneActions();
            detach(releaseAllPruneLeases());
            removeEventListener("prune_progress", pruneProgressListener);
            removeEventListener("prune_complete", pruneCompleteListener);
        },
    };
});

export { index as default };
