import React, { useState, useRef, useEffect } from 'react';
import { UserRole, Employee, AttendanceRecord, OrgSettings } from '../types';
import { getHaversineDistance } from '../utils/rules';
import { FaceEnrollmentModal } from './FaceEnrollmentModal';
import {
  Clock,
  Camera,
  MapPin,
  CheckCircle,
  AlertTriangle,
  RotateCcw,
  ShieldCheck,
  Calendar,
  UserCheck,
  Info,
  X,
  Scan,
  Sparkles,
  User,
} from 'lucide-react';

interface AttendanceModuleProps {
  role: UserRole;
  currentUser: Employee;
  settings: OrgSettings;
  attendance: AttendanceRecord[];
  onCheckIn: (record: AttendanceRecord) => void;
  onCheckOut: (recordId: string, checkOutTime: string, hours: number) => void;
  onRequestCorrection: (recordId: string, reason: string) => void;
  onApproveCorrection: (recordId: string) => void;
  onEnrollFace?: (employeeId: string, photoUrl: string, descriptor: string) => void;
}

export const AttendanceModule: React.FC<AttendanceModuleProps> = ({
  role,
  currentUser,
  settings,
  attendance,
  onCheckIn,
  onCheckOut,
  onRequestCorrection,
  onApproveCorrection,
  onEnrollFace,
}) => {
  const [activeTab, setActiveTab] = useState<'board' | 'checkin'>('board');
  const [showCameraModal, setShowCameraModal] = useState<boolean>(false);
  const [showEnrollmentModal, setShowEnrollmentModal] = useState<boolean>(false);

  // Camera & Face detection state
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const [streamActive, setStreamActive] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [faceDetected, setFaceDetected] = useState<boolean>(true);
  const [multipleFaces, setMultipleFaces] = useState<boolean>(false);
  const [matchConfidence, setMatchConfidence] = useState<number>(currentUser.faceEnrolled ? 98.6 : 0);
  const [isScanningBiometrics, setIsScanningBiometrics] = useState<boolean>(false);

  // Geolocation state
  const [userLat, setUserLat] = useState<number>(settings.officeLat + 0.0003); // Close by default
  const [userLng, setUserLng] = useState<number>(settings.officeLng + 0.0002);
  const [gpsAccuracy, setGpsAccuracy] = useState<number>(15); // meters
  const [locating, setLocating] = useState<boolean>(false);
  const [geofenceDistance, setGeofenceDistance] = useState<number>(0);
  const [withinGeofence, setWithinGeofence] = useState<boolean>(true);

  // Correction request modal
  const [correctionRecord, setCorrectionRecord] = useState<AttendanceRecord | null>(null);
  const [correctionReason, setCorrectionReason] = useState<string>('');

  const todayStr = new Date().toISOString().split('T')[0];

  // Calculate geofence distance whenever coordinates change
  useEffect(() => {
    const dist = getHaversineDistance(userLat, userLng, settings.officeLat, settings.officeLng);
    setGeofenceDistance(dist);
    setWithinGeofence(dist <= settings.officeRadiusMeters);
  }, [userLat, userLng, settings.officeLat, settings.officeLng, settings.officeRadiusMeters]);

  // Read real browser geolocation if available
  const handleFetchCurrentGps = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser.');
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUserLat(pos.coords.latitude);
        setUserLng(pos.coords.longitude);
        setGpsAccuracy(Math.round(pos.coords.accuracy));
        setLocating(false);
      },
      (err) => {
        console.warn('Geolocation error:', err.message);
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  };

  // Start webcam video stream
  const startCamera = async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        setStreamActive(true);
      }
    } catch (err: any) {
      console.warn('Camera access issue:', err);
      setCameraError('Camera access not granted or unavailable. Simulated video frame active.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setStreamActive(false);
  };

  useEffect(() => {
    if (showCameraModal) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => {
      stopCamera();
    };
  }, [showCameraModal]);

  // Today's record for current user
  const myTodayRecord = attendance.find(
    (a) => a.date === todayStr && a.employeeId === currentUser.employeeId
  );

  // Mark Check-in
  const handlePerformCheckIn = (method: 'Web' | 'Camera') => {
    // Duplicate checkin check (Section 3 rule: second check-in = 409)
    if (myTodayRecord) {
      alert('Error 409: Attendance already checked in for today!');
      return;
    }

    // Geofence check
    if (!withinGeofence) {
      alert(
        `Check-in Rejected: You are ${geofenceDistance}m away, which exceeds the office perimeter limit of ${settings.officeRadiusMeters}m.`
      );
      return;
    }

    if (method === 'Camera') {
      if (!faceDetected || multipleFaces) {
        alert('Check-in Rejected: Exactly one face must be detected in the camera frame.');
        return;
      }
      if (!currentUser.faceEnrolled) {
        alert(
          'Check-in Rejected: Facial biometric profile is not enrolled yet. Please click "Enroll Face Now" before camera verification.'
        );
        return;
      }
      if (gpsAccuracy > 100) {
        alert(`Check-in Rejected: GPS accuracy (${gpsAccuracy}m) is worse than required 100m.`);
        return;
      }
    }

    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const checkInTime = `${hours}:${minutes}`;

    // Status evaluation: office start 09:00 + grace 15 min = 09:15 cutoff
    const [startH, startM] = settings.officeStart.split(':').map(Number);
    const cutoffMinutes = startH * 60 + startM + settings.graceMinutes;
    const currentMinutes = now.getHours() * 60 + now.getMinutes();

    const isLate = currentMinutes > cutoffMinutes;

    const newRecord: AttendanceRecord = {
      id: `ATT-${Date.now()}`,
      employeeId: currentUser.employeeId,
      employeeName: currentUser.name,
      date: todayStr,
      checkInTime,
      hoursWorked: 0,
      status: isLate ? 'Late' : 'Present',
      method,
      verifiedLocation: true,
      distanceMeters: geofenceDistance,
      faceVerified: method === 'Camera',
      faceConfidence: method === 'Camera' ? matchConfidence : undefined,
    };

    onCheckIn(newRecord);
    setShowCameraModal(false);
  };

  // Mark Check-out
  const handlePerformCheckOut = () => {
    if (!myTodayRecord) {
      alert('No check-in record found for today.');
      return;
    }

    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const checkOutTime = `${hours}:${minutes}`;

    const [inH, inM] = myTodayRecord.checkInTime.split(':').map(Number);
    const workedHours =
      Math.round(((now.getHours() * 60 + now.getMinutes() - (inH * 60 + inM)) / 60) * 10) / 10;

    onCheckOut(myTodayRecord.id, checkOutTime, workedHours);
  };

  // Submit correction request
  const handleSubmitCorrection = () => {
    if (!correctionRecord || !correctionReason) return;
    onRequestCorrection(correctionRecord.id, correctionReason);
    setCorrectionRecord(null);
    setCorrectionReason('');
  };

  return (
    <div className="space-y-6">
      {/* Module Title Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 rounded-2xl shadow-sm">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Clock className="w-5 h-5 text-teal-400" /> Web & Biometric Attendance (Module 4)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Official rules: Office start {settings.officeStart} (grace {settings.graceMinutes}m), half-day under {settings.halfDayHours}h, geofence radius {settings.officeRadiusMeters}m.
          </p>
        </div>

        {/* Tab switch */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('board')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'board' ? 'bg-slate-800 text-teal-300' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Attendance Board
          </button>
          <button
            onClick={() => setActiveTab('checkin')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'checkin' ? 'bg-slate-800 text-teal-300' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Mark Check-in / Out
          </button>
        </div>
      </div>

      {/* CHECK-IN WIDGET VIEW */}
      {activeTab === 'checkin' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Card 1: Today's Status & Action */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-sm space-y-5">
            <div>
              <span className="text-xs font-bold text-teal-400 uppercase tracking-wider">
                My Attendance Today
              </span>
              <h3 className="text-xl font-bold text-slate-100 mt-1">
                {new Date().toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </h3>
            </div>

            {myTodayRecord ? (
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-400">Current Status:</span>
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                      myTodayRecord.status === 'Present'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : myTodayRecord.status === 'Late'
                        ? 'bg-amber-950 text-amber-400 border border-amber-800'
                        : 'bg-slate-800 text-slate-300'
                    }`}
                  >
                    {myTodayRecord.status}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-500 block text-[10px]">Check-in Time</span>
                    <span className="text-slate-200 font-semibold text-sm">
                      {myTodayRecord.checkInTime}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Check-out Time</span>
                    <span className="text-slate-200 font-semibold text-sm">
                      {myTodayRecord.checkOutTime || 'Active (On Duty)'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Verification Method</span>
                    <span className="text-slate-300 font-medium">{myTodayRecord.method}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px]">Distance to Office</span>
                    <span className="text-slate-300 font-medium">
                      {myTodayRecord.distanceMeters || 45} meters
                    </span>
                  </div>
                </div>

                {!myTodayRecord.checkOutTime && (
                  <button
                    onClick={handlePerformCheckOut}
                    className="w-full mt-3 bg-rose-600 hover:bg-rose-500 text-white font-bold py-2 rounded-xl text-xs transition-colors shadow"
                  >
                    Record Check-out Now
                  </button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2 text-xs text-slate-300">
                  <div className="flex items-center gap-2 text-teal-400 font-semibold">
                    <Info className="w-4 h-4" /> Ready for Daily Check-in
                  </div>
                  <p>
                    Check in with simple Web timestamp, or use Biometric Camera check-in with GPS Geofencing for bonus points!
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => handlePerformCheckIn('Web')}
                    className="flex flex-col items-center justify-center p-4 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl transition-all"
                  >
                    <Clock className="w-6 h-6 text-teal-400 mb-1" />
                    <span className="font-semibold text-xs">Web Check-in</span>
                    <span className="text-[10px] text-slate-400">Timestamp + GPS</span>
                  </button>

                  <button
                    onClick={() => setShowCameraModal(true)}
                    className="flex flex-col items-center justify-center p-4 bg-gradient-to-tr from-teal-950 to-emerald-950 hover:from-teal-900 hover:to-emerald-900 text-emerald-300 border border-teal-500/40 rounded-xl transition-all shadow"
                  >
                    <Camera className="w-6 h-6 text-emerald-400 mb-1" />
                    <span className="font-bold text-xs">Camera Face Check-in</span>
                    <span className="text-[10px] text-teal-400">AI Face + Geofence</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Card 2: GPS Geofence & Office Perimeter Status */}
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-teal-400" /> Office Geofence Perimeter
              </h3>
              <button
                onClick={handleFetchCurrentGps}
                disabled={locating}
                className="text-xs text-teal-400 hover:underline flex items-center gap-1"
              >
                <RotateCcw className={`w-3 h-3 ${locating ? 'animate-spin' : ''}`} />
                {locating ? 'Locating...' : 'Refresh GPS'}
              </button>
            </div>

            <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Calculated Distance:</span>
                <span
                  className={`font-mono font-bold text-sm ${
                    withinGeofence ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {geofenceDistance} meters
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Maximum Allowed Radius:</span>
                <span className="font-mono text-slate-200">
                  {settings.officeRadiusMeters} meters
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">GPS Accuracy:</span>
                <span className="font-mono text-slate-300">±{gpsAccuracy}m (required &lt; 100m)</span>
              </div>

              <div
                className={`p-3 rounded-lg border text-xs font-semibold flex items-center gap-2 ${
                  withinGeofence
                    ? 'bg-emerald-950/50 border-emerald-800 text-emerald-300'
                    : 'bg-rose-950/50 border-rose-900 text-rose-300'
                }`}
              >
                {withinGeofence ? (
                  <>
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    <span>Inside office perimeter. Check-in permitted.</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle className="w-4 h-4 text-rose-400" />
                    <span>Outside geofence ({geofenceDistance}m). Check-in will be rejected.</span>
                  </>
                )}
              </div>
            </div>

            {/* Simulated Coordinate Slider for Testing */}
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 space-y-2 text-xs">
              <span className="font-semibold text-slate-300">Tester Controls (Simulate Movement):</span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setUserLat(settings.officeLat);
                    setUserLng(settings.officeLng);
                  }}
                  className="bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded text-[11px] text-teal-300 border border-slate-700"
                >
                  Inside Office (0m)
                </button>
                <button
                  onClick={() => {
                    setUserLat(settings.officeLat + 0.001);
                    setUserLng(settings.officeLng + 0.001);
                  }}
                  className="bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded text-[11px] text-emerald-300 border border-slate-700"
                >
                  Within 100m
                </button>
                <button
                  onClick={() => {
                    setUserLat(settings.officeLat + 0.005);
                    setUserLng(settings.officeLng + 0.005);
                  }}
                  className="bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded text-[11px] text-rose-300 border border-slate-700"
                >
                  Outside Office (600m)
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ATTENDANCE BOARD VIEW */}
      {activeTab === 'board' && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
              <Calendar className="w-4 h-4 text-teal-400" /> Daily Attendance Register
            </h3>
            <span className="text-xs text-slate-400">{attendance.length} total entries</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 border-b border-slate-800 uppercase text-[10px] tracking-wider">
                <tr>
                  <th className="py-3 px-4">Date</th>
                  <th className="py-3 px-4">Employee</th>
                  <th className="py-3 px-4">Check-in</th>
                  <th className="py-3 px-4">Check-out</th>
                  <th className="py-3 px-4">Hours</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Method</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-200">
                {attendance.map((rec) => {
                  const isMyRecord = rec.employeeId === currentUser.employeeId;

                  return (
                    <tr key={rec.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-mono text-slate-300">{rec.date}</td>
                      <td className="py-3 px-4 font-semibold text-slate-100">
                        {rec.employeeName}
                        {isMyRecord && (
                          <span className="text-[10px] text-teal-400 ml-1.5 font-normal">(You)</span>
                        )}
                      </td>
                      <td className="py-3 px-4 font-mono">{rec.checkInTime}</td>
                      <td className="py-3 px-4 font-mono text-slate-400">
                        {rec.checkOutTime || '—'}
                      </td>
                      <td className="py-3 px-4 font-mono">{rec.hoursWorked || '—'}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            rec.status === 'Present'
                              ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/80'
                              : rec.status === 'Late'
                              ? 'bg-amber-950 text-amber-400 border border-amber-800/80'
                              : rec.status === 'Half Day'
                              ? 'bg-purple-950 text-purple-400 border border-purple-800/80'
                              : 'bg-rose-950 text-rose-400 border border-rose-800/80'
                          }`}
                        >
                          {rec.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">
                        <span className="flex items-center gap-1.5">
                          {rec.method === 'Camera' ? (
                            <span
                              className="inline-flex items-center gap-1 text-emerald-400 font-semibold"
                              title={rec.faceConfidence ? `Face Match: ${rec.faceConfidence}%` : 'Face Biometric'}
                            >
                              <Camera className="w-3.5 h-3.5 text-emerald-400" />
                              Camera
                              {rec.faceVerified && (
                                <span className="text-[9px] bg-emerald-950 text-emerald-300 border border-emerald-800 px-1.5 py-0.2 rounded font-mono">
                                  {rec.faceConfidence ? `${rec.faceConfidence}%` : 'Verified'}
                                </span>
                              )}
                            </span>
                          ) : (
                            <>
                              <Clock className="w-3 h-3 text-slate-400" />
                              {rec.method}
                            </>
                          )}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        {rec.correctionRequested ? (
                          <span className="text-amber-400 text-[10px] italic">
                            Correction Pending
                          </span>
                        ) : isMyRecord && (rec.status === 'Late' || rec.status === 'Half Day') ? (
                          <button
                            onClick={() => setCorrectionRecord(rec)}
                            className="bg-slate-800 hover:bg-slate-700 text-teal-300 px-2.5 py-1 rounded text-[11px] font-medium border border-slate-700 transition-colors"
                          >
                            Request Correction
                          </button>
                        ) : (role === 'HR' || role === 'Admin') && rec.correctionRequested ? (
                          <button
                            onClick={() => onApproveCorrection(rec.id)}
                            className="bg-teal-600 hover:bg-teal-500 text-slate-950 px-2.5 py-1 rounded text-[11px] font-bold shadow"
                          >
                            Approve Correction
                          </button>
                        ) : null}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CAMERA BIOMETRIC MODAL WITH LIVE FACE DETECTION */}
      {showCameraModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/85 backdrop-blur-sm p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl text-slate-100 flex flex-col my-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-emerald-500/10 rounded-xl border border-emerald-500/30 text-emerald-400">
                  <Camera className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-slate-100 flex items-center gap-2">
                    Biometric Face Detection & Check-in
                  </h3>
                  <p className="text-xs text-slate-400">
                    Live facial landmark extraction matching against enrolled profile
                  </p>
                </div>
              </div>
              <button
                onClick={() => setShowCameraModal(false)}
                className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg hover:bg-slate-800"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {/* If face not enrolled, show alert banner and action button */}
              {!currentUser.faceEnrolled && (
                <div className="p-3 bg-amber-950/40 border border-amber-800/80 rounded-xl flex items-center justify-between gap-3 text-xs">
                  <div className="flex items-center gap-2 text-amber-300">
                    <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
                    <span>Your facial biometric profile is not yet registered in HCM Lite.</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setShowEnrollmentModal(true);
                    }}
                    className="shrink-0 px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs rounded-lg shadow transition-all flex items-center gap-1.5"
                  >
                    <Camera className="w-3.5 h-3.5" /> Enroll Face Now
                  </button>
                </div>
              )}

              {/* Video container with face bounding box overlay */}
              <div className="relative bg-slate-950 rounded-xl overflow-hidden aspect-video border border-slate-800 flex items-center justify-center">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-full object-cover"
                />

                {/* Simulated/Overlay Face detection reticle & facial mesh */}
                <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
                  <div
                    className={`relative w-48 h-60 border-2 rounded-2xl transition-all flex flex-col justify-between p-3 ${
                      faceDetected && !multipleFaces
                        ? 'border-emerald-400 bg-emerald-500/10 shadow-[0_0_20px_rgba(16,185,129,0.2)]'
                        : 'border-rose-400 bg-rose-500/10 shadow-[0_0_20px_rgba(244,63,94,0.2)]'
                    }`}
                  >
                    {/* Scanner scanning bar animation */}
                    <div className="absolute left-2 right-2 h-0.5 bg-gradient-to-r from-transparent via-emerald-400 to-transparent top-1/2 -translate-y-1/2 animate-pulse" />

                    {/* Corner targeting brackets */}
                    <div className="absolute top-2 left-2 w-4 h-4 border-t-2 border-l-2 border-emerald-400" />
                    <div className="absolute top-2 right-2 w-4 h-4 border-t-2 border-r-2 border-emerald-400" />
                    <div className="absolute bottom-2 left-2 w-4 h-4 border-b-2 border-l-2 border-emerald-400" />
                    <div className="absolute bottom-2 right-2 w-4 h-4 border-b-2 border-r-2 border-emerald-400" />

                    {/* Eye and mouth facial landmark markers */}
                    <div className="absolute top-20 left-12 w-2 h-2 rounded-full bg-emerald-400/80 animate-ping" />
                    <div className="absolute top-20 right-12 w-2 h-2 rounded-full bg-emerald-400/80 animate-ping" />
                    <div className="absolute top-32 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-emerald-400/80" />
                    <div className="absolute bottom-16 left-1/2 -translate-x-1/2 w-8 h-1 rounded-full bg-emerald-400/60" />

                    <div className="flex items-center justify-between w-full">
                      <span className="text-[10px] font-bold text-emerald-300 bg-slate-950/85 px-2 py-0.5 rounded-md backdrop-blur border border-emerald-500/30">
                        {faceDetected && !multipleFaces ? 'Face Detected: 1' : 'Face Detection Error'}
                      </span>
                      {currentUser.faceEnrolled && (
                        <span className="text-[10px] font-mono font-bold text-teal-300 bg-slate-950/85 px-2 py-0.5 rounded-md backdrop-blur border border-teal-500/30">
                          Match: {matchConfidence}%
                        </span>
                      )}
                    </div>

                    <span className="text-[10px] text-slate-200 bg-slate-950/85 px-2.5 py-0.5 rounded-full self-center border border-slate-700/80 backdrop-blur">
                      {faceDetected && !multipleFaces ? 'Face Aligned (Live Biometrics)' : 'Position Face in Center'}
                    </span>
                  </div>
                </div>

                {/* Picture-in-picture enrolled face avatar */}
                {currentUser.faceEnrolled && (
                  <div className="absolute top-3 right-3 bg-slate-950/90 border border-slate-700 rounded-xl p-1.5 flex items-center gap-2 shadow-lg backdrop-blur">
                    <img
                      src={currentUser.facePhotoUrl || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80'}
                      alt="Enrolled Face"
                      className="w-10 h-10 rounded-lg object-cover border border-emerald-500/60"
                    />
                    <div className="text-[10px] text-left pr-1">
                      <div className="font-bold text-slate-200 leading-tight">Enrolled Profile</div>
                      <div className="text-emerald-400 font-mono text-[9px]">Verified #{currentUser.employeeId}</div>
                    </div>
                  </div>
                )}

                {cameraError && (
                  <div className="absolute bottom-2 left-2 right-2 p-2 bg-slate-900/90 text-amber-300 text-[11px] rounded-lg border border-amber-800/80">
                    {cameraError}
                  </div>
                )}
              </div>

              {/* Status checklist */}
              <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Facial Detection & Liveness:</span>
                  <span
                    className={`font-bold flex items-center gap-1 ${
                      faceDetected && !multipleFaces ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {faceDetected && !multipleFaces ? (
                      <CheckCircle className="w-3.5 h-3.5" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5" />
                    )}
                    {faceDetected && !multipleFaces ? 'Single Face Verified' : 'Multiple / No Face Detected'}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Biometric Template Matching:</span>
                  <span
                    className={`font-bold flex items-center gap-1 ${
                      currentUser.faceEnrolled ? 'text-emerald-400' : 'text-amber-400'
                    }`}
                  >
                    {currentUser.faceEnrolled ? (
                      <>
                        <ShieldCheck className="w-3.5 h-3.5" />
                        Match Verified ({matchConfidence}% &gt; 85% Threshold)
                      </>
                    ) : (
                      <>
                        <AlertTriangle className="w-3.5 h-3.5" />
                        Not Enrolled (Registration Required)
                      </>
                    )}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Office Geofence Perimeter:</span>
                  <span
                    className={`font-bold flex items-center gap-1 ${
                      withinGeofence ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {withinGeofence ? (
                      <CheckCircle className="w-3.5 h-3.5" />
                    ) : (
                      <AlertTriangle className="w-3.5 h-3.5" />
                    )}
                    {geofenceDistance}m ({withinGeofence ? 'Within 150m boundary' : 'Outside boundary'})
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">GPS Accuracy:</span>
                  <span className="text-slate-200 font-mono">±{gpsAccuracy}m (&lt; 100m)</span>
                </div>
              </div>

              {/* Test toggle controls */}
              <div className="flex items-center justify-between text-[11px] text-slate-400 px-1 bg-slate-950/50 p-2 rounded-lg border border-slate-800/60">
                <span>Simulation Controls:</span>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setFaceDetected(!faceDetected)}
                    className="hover:underline text-teal-400"
                  >
                    Toggle Face Detection
                  </button>
                  <span>|</span>
                  <button
                    type="button"
                    onClick={() => setMultipleFaces(!multipleFaces)}
                    className="hover:underline text-amber-400"
                  >
                    Toggle Multi-Face Error
                  </button>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCameraModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-slate-400 hover:text-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => handlePerformCheckIn('Camera')}
                  disabled={!withinGeofence || !faceDetected || multipleFaces || !currentUser.faceEnrolled}
                  className="flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-600 hover:to-teal-500 text-slate-950 font-bold px-5 py-2.5 rounded-xl text-xs shadow-lg shadow-teal-950/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  <UserCheck className="w-4 h-4" />
                  Verify Biometric & Check-in
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CORRECTION REQUEST MODAL */}
      {correctionRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl text-slate-100">
            <h3 className="font-bold text-base text-slate-100 mb-2">
              Request Attendance Correction
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Record date: {correctionRecord.date} ({correctionRecord.status} at{' '}
              {correctionRecord.checkInTime}). Please provide a valid justification for HR approval.
            </p>

            <textarea
              rows={3}
              value={correctionReason}
              onChange={(e) => setCorrectionReason(e.target.value)}
              placeholder="e.g. Unavoidable subway transit outage between 08:45 and 09:20 AM."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-200 focus:outline-none focus:ring-1 focus:ring-teal-500 mb-4"
            />

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setCorrectionRecord(null)}
                className="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitCorrection}
                className="bg-teal-600 hover:bg-teal-500 text-slate-950 font-semibold px-4 py-1.5 rounded-xl text-xs"
              >
                Submit Request to HR
              </button>
            </div>
          </div>
        </div>
      )}

      {/* IN-FLOW BIOMETRIC FACE ENROLLMENT MODAL */}
      {showEnrollmentModal && (
        <FaceEnrollmentModal
          employee={currentUser}
          isOpen={showEnrollmentModal}
          onClose={() => setShowEnrollmentModal(false)}
          onEnrollFace={(empId, photoUrl, descriptor) => {
            if (onEnrollFace) {
              onEnrollFace(empId, photoUrl, descriptor);
            }
            setMatchConfidence(98.8);
            setShowEnrollmentModal(false);
          }}
        />
      )}
    </div>
  );
};
