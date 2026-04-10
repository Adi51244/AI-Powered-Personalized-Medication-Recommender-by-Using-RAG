'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'

interface PatientProfile {
  user_id: string
  display_name: string
  email: string
  created_at: string
  total_diagnoses: number
}

export function AdminDashboard({ userId }: { userId: string }) {
  const [patients, setPatients] = useState<PatientProfile[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [totalStats, setTotalStats] = useState({
    totalPatients: 0,
    totalDiagnoses: 0,
    totalMedications: 0,
  })

  useEffect(() => {
    const fetchAllPatients = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/v1/patients`
        )
        if (response.ok) {
          const data = await response.json()
          const patientList = data.patients || []
          setPatients(patientList)

          // Calculate stats
          const totalDiagnoses = patientList.reduce(
            (sum: number, p: any) => sum + (p.total_diagnoses || 0),
            0
          )

          setTotalStats({
            totalPatients: patientList.length,
            totalDiagnoses,
            totalMedications: totalDiagnoses, // Can be updated with actual data
          })
        }
      } catch (error) {
        console.error('Failed to fetch patients:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAllPatients()
  }, [])

  const filteredPatients = patients.filter(
    (p) =>
      p.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.email.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <Tabs defaultValue="overview" className="w-full">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="patients">All Patients</TabsTrigger>
      </TabsList>

      {/* Overview Tab */}
      <TabsContent value="overview" className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Patients
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{totalStats.totalPatients}</div>
              <p className="text-xs text-gray-500 mt-1">registered users</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Diagnoses
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{totalStats.totalDiagnoses}</div>
              <p className="text-xs text-gray-500 mt-1">across all patients</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Platform Health
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">100%</div>
              <p className="text-xs text-gray-500 mt-1">system operational</p>
            </CardContent>
          </Card>
        </div>
      </TabsContent>

      {/* Patients Tab */}
      <TabsContent value="patients" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Patient Directory</CardTitle>
            <CardDescription>
              Manage and view all patient profiles
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              placeholder="Search by name or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-gray-50"
            />

            {filteredPatients.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No patients found</p>
            ) : (
              <div className="rounded-lg border overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-left font-semibold">Name</th>
                      <th className="px-4 py-3 text-left font-semibold">Email</th>
                      <th className="px-4 py-3 text-left font-semibold">Diagnoses</th>
                      <th className="px-4 py-3 text-left font-semibold">Joined</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredPatients.map((patient) => (
                      <tr key={patient.user_id} className="border-b hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium">{patient.display_name}</td>
                        <td className="px-4 py-3 text-gray-600">{patient.email}</td>
                        <td className="px-4 py-3">{patient.total_diagnoses || 0}</td>
                        <td className="px-4 py-3 text-gray-500">
                          {new Date(patient.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  )
}
