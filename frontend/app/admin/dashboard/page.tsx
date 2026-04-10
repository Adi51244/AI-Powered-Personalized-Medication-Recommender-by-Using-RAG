'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth/context';
import { redirect } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { LogOut, Search, Users, TrendingUp } from 'lucide-react';
import Container from '@/components/layout/Container';

interface PatientProfile {
  id: string;
  email: string;
  name?: string;
  ageGroup?: string;
  gender?: string;
  diagnosisCount: number;
  lastActivity?: string;
  riskLevel?: 'low' | 'medium' | 'high';
}

export default function AdminDashboardPage() {
  const { user, loading, signOut, isAdmin } = useAuth();
  const [patients, setPatients] = useState<PatientProfile[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [stats, setStats] = useState({
    totalPatients: 0,
    activeDiagnoses: 0,
    avgDiagnosesPerPatient: 0,
  });

  useEffect(() => {
    if (!loading && (!user || !isAdmin)) {
      redirect('/dashboard');
    }
  }, [user, loading, isAdmin]);

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await fetch('/api/v1/patients');
        const data = await response.json();
        setPatients(data || []);

        setStats({
          totalPatients: data?.length || 0,
          activeDiagnoses: data?.reduce((sum: number, p: PatientProfile) => sum + p.diagnosisCount, 0) || 0,
          avgDiagnosesPerPatient: data?.length > 0
            ? (data.reduce((sum: number, p: PatientProfile) => sum + p.diagnosisCount, 0) / data.length).toFixed(1)
            : 0,
        });
      } catch (error) {
        console.error('Failed to fetch patients:', error);
      } finally {
        setLoadingData(false);
      }
    };

    if (user && isAdmin) {
      fetchPatients();
    }
  }, [user, isAdmin]);

  if (loading || !user || !isAdmin) {
    return null;
  }

  const filteredPatients = patients.filter((p) =>
    p.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Container>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Admin Dashboard</h1>
            <p className="text-gray-600 mt-1">Manage all patients and view analytics</p>
          </div>
          <Button variant="outline" onClick={signOut}>
            <LogOut className="mr-2 h-4 w-4" />
            Sign Out
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Patients</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end justify-between">
                <div>
                  <div className="text-3xl font-bold">{stats.totalPatients}</div>
                  <p className="text-xs text-gray-500 mt-1">registered users</p>
                </div>
                <Users className="h-8 w-8 text-blue-500 opacity-20" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Diagnoses</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end justify-between">
                <div>
                  <div className="text-3xl font-bold">{stats.activeDiagnoses}</div>
                  <p className="text-xs text-gray-500 mt-1">across all patients</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-500 opacity-20" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Avg per Patient</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.avgDiagnosesPerPatient}</div>
              <p className="text-xs text-gray-500 mt-1">diagnoses per patient</p>
            </CardContent>
          </Card>
        </div>

        {/* Search and Filter */}
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search by email or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        {/* Patients Table */}
        <Card>
          <CardHeader>
            <CardTitle>Patient Profiles</CardTitle>
            <CardDescription>Complete list of all registered patients</CardDescription>
          </CardHeader>
          <CardContent>
            {loadingData ? (
              <p className="text-gray-600">Loading...</p>
            ) : filteredPatients.length === 0 ? (
              <p className="text-gray-600 text-center py-8">No patients found</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="border-b bg-gray-50">
                    <tr>
                      <th className="text-left px-4 py-2 font-medium text-sm">Patient</th>
                      <th className="text-left px-4 py-2 font-medium text-sm">Email</th>
                      <th className="text-left px-4 py-2 font-medium text-sm">Age Group</th>
                      <th className="text-left px-4 py-2 font-medium text-sm">Diagnoses</th>
                      <th className="text-left px-4 py-2 font-medium text-sm">Risk Level</th>
                      <th className="text-left px-4 py-2 font-medium text-sm">Last Activity</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPatients.map((patient) => (
                      <tr key={patient.id} className="border-b hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium">{patient.name || 'N/A'}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{patient.email}</td>
                        <td className="px-4 py-3 text-sm">{patient.ageGroup || 'N/A'}</td>
                        <td className="px-4 py-3 font-medium">{patient.diagnosisCount}</td>
                        <td className="px-4 py-3">
                          {patient.riskLevel && (
                            <Badge
                              variant={
                                patient.riskLevel === 'high'
                                  ? 'destructive'
                                  : patient.riskLevel === 'medium'
                                  ? 'secondary'
                                  : 'default'
                              }
                            >
                              {patient.riskLevel}
                            </Badge>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {patient.lastActivity ? new Date(patient.lastActivity).toLocaleDateString() : 'N/A'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </Container>
  );
}
