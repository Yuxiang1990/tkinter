import pandas as pd
from glob import glob
import pydicom as dicom
import os
import SimpleITK as sitk


# This file will parse the dir, extract the right CT_series, and convert to arr

class Series(object):
    def __init__(self, candidate_paths, seriesuid=None):
        columns = ['study_uid', 'series_uid', 'sop_uid', 'access_num', 'instance_num', 'slice_thickness',
                   'ImagePosition_Z', 'w_center', 'w_width',
                   'PatientID', 'PatientName', 'PatientBirthDate', 'PatientSex',
                   'StudyDate', 'StudyTime', 'AcquisitionTime',
                   'InstitutionName', 'Manufacturer',
                   'SOPClassUID',
                   'path']
        self.series_df = pd.DataFrame(columns=columns)
        self.candidate_paths = candidate_paths
        self.series_uid = seriesuid
        index = 0
        # create_series_df
        for cand in self.candidate_paths:
            cand_files = glob(cand + "/*")
            for cf in cand_files:
                try:
                    # ds = dicom.read_file(cf)
                    ds = sitk.ReadImage(cf)
                    index += 1
                    self.series_df.loc[index, 'path'] = cf
                    # self.series_df.loc[index,'study_uid'] = self._get_attr(ds,"StudyInstanceUID")#'0020|000d'
                    # self.series_df.loc[index,'series_uid'] = self._get_attr(ds,"SeriesInstanceUID")#'0020|000e'
                    # self.series_df.loc[index,'sop_uid'] = self._get_attr(ds,"SOPInstanceUID")#'0008|0018'
                    # self.series_df.loc[index,'instance_num'] = self._get_attr(ds,"InstanceNumber")#'0020|0013'
                    # self.series_df.loc[index,'ImagePosition_Z'] = self._get_attr(ds,"ImagePositionPatient")[2]#'0020|0032'
                    # self.series_df.loc[index,'w_center'] = self._get_attr(ds,"WindowCenter")#'0028|1050'
                    # self.series_df.loc[index,'w_width'] = self._get_attr(ds,"WindowWidth")#'0028|1051'

                    # self.series_df.loc[index,'PatientID'] = self._get_attr(ds,"PatientID")#'0010|0020'
                    # self.series_df.loc[index,'PatientName'] = str(self._get_attr(ds,"PatientName"))#'0010|0010'
                    # self.series_df.loc[index,'PatientBirthDate'] = self._get_attr(ds,"PatientBirthDate")#'0010|0030'
                    # self.series_df.loc[index,'PatientSex'] = self._get_attr(ds,"PatientSex")#'0010|0040'
                    # self.series_df.loc[index,'PatientAge'] = self._get_attr(ds,"PatientAge")#'0010|1010'

                    # self.series_df.loc[index,'StudyDate'] = self._get_attr(ds,"StudyDate")#'0008|0020'
                    # self.series_df.loc[index,'StudyTime'] = self._get_attr(ds,"StudyTime")#'0008|0030'
                    # self.series_df.loc[index,'InstitutionName'] = self._get_attr(ds,"InstitutionName")#'0008|0080'
                    # self.series_df.loc[index,'Manufacturer'] = self._get_attr(ds,"Manufacturer")#'0008|0070'
                    # self.series_df.loc[index,'PatientPosition'] = self._get_attr(ds,"PatientPosition")#'0018|5100'
                    # self.series_df.loc[index,'SOPClassUID'] = self._get_attr(ds,"SOPClassUID")#'0008|0016'
                    keys = ds.GetMetaDataKeys()
                    self.series_df.loc[index, 'study_uid'] = self._getmetadata(ds, keys, '0020|000d')
                    self.series_df.loc[index, 'series_uid'] = self._getmetadata(ds, keys, '0020|000e')
                    self.series_df.loc[index, 'sop_uid'] = self._getmetadata(ds, keys, '0008|0018')
                    self.series_df.loc[index, 'access_num'] = self._getmetadata(ds, keys, '0008|0050')
                    self.series_df.loc[index, 'instance_num'] = int(self._getmetadata(ds, keys, '0020|0013'))
                    slice_thickness = self._getmetadata(ds, keys, '0018|0050')
                    if slice_thickness is not None:
                        self.series_df.loc[index, 'slice_thickness'] = float(slice_thickness)
                    else:
                        self.series_df.loc[index, 'slice_thickness'] = slice_thickness
                    self.series_df.loc[index, 'ImagePosition_Z'] = float(
                        self._getmetadata(ds, keys, '0020|0032').split("\\")[2])
                    self.series_df.loc[index, 'w_center'] = self._getmetadata(ds, keys, '0028|1050')
                    self.series_df.loc[index, 'w_width'] = self._getmetadata(ds, keys, '0028|1051')

                    self.series_df.loc[index, 'PatientID'] = self._getmetadata(ds, keys, '0010|0020')
                    self.series_df.loc[index, 'PatientBirthDate'] = self._getmetadata(ds, keys, '0010|0030')
                    self.series_df.loc[index, 'PatientSex'] = self._getmetadata(ds, keys, '0010|0040')
                    self.series_df.loc[index, 'PatientAge'] = self._getmetadata(ds, keys, '0010|1010')

                    self.series_df.loc[index, 'StudyDate'] = self._getmetadata(ds, keys, '0008|0020')
                    self.series_df.loc[index, 'StudyTime'] = self._getmetadata(ds, keys, '0008|0030')
                    self.series_df.loc[index, 'AcquisitionTime'] = self._getmetadata(ds, keys, '0008|0032')
                    self.series_df.loc[index, 'Manufacturer'] = self._getmetadata(ds, keys, '0008|0070')
                    self.series_df.loc[index, 'PatientPosition'] = self._getmetadata(ds, keys, '0018|5100')
                    self.series_df.loc[index, 'SOPClassUID'] = self._getmetadata(ds, keys, '0008|0016')
                    try:
                        patient_name = self._getmetadata(ds, keys, '0010|0010')
                        patient_name.encode('utf8')
                        self.series_df.loc[index, 'PatientName'] = patient_name
                    except:
                        try:
                            pydicom = dicom.read_file(cf)
                            self.series_df.loc[index, 'PatientName'] = str(self._get_attr(pydicom, "PatientName"))
                        except:
                            self.series_df.loc[index, 'PatientName'] = None
                    try:
                        InstitutionName = self._getmetadata(ds, keys, '0008|0080')
                        InstitutionName.encode('utf8')
                        self.series_df.loc[index, 'InstitutionName'] = InstitutionName
                    except:
                        try:
                            pydicom = dicom.read_file(cf)
                            self.series_df.loc[index, 'InstitutionName'] = self._get_attr(pydicom, "InstitutionName")
                        except:
                            self.series_df.loc[index, 'InstitutionName'] = None
                except Exception as e:
                    cf_name = os.path.basename(cf)
                    print("%s create failed,%s" % (cf_name, e))

        # bug20180420 drop duplicates
        keys = ['study_uid', 'series_uid', 'ImagePosition_Z', 'instance_num']
        self.series_df = self.series_df.sort_values(by=keys).drop_duplicates(keys[:3])

        print("Series_df init ok, success create series_candidate_df")

        try:
            if self.series_uid is None:
                series_df_count = self.series_df.groupby(['study_uid', 'series_uid']).count().reset_index()
                self.study_uid = \
                    series_df_count[series_df_count['sop_uid'] == series_df_count['sop_uid'].max()]['study_uid'].values[
                        0]
                self.series_uid = \
                    series_df_count[series_df_count['sop_uid'] == series_df_count['sop_uid'].max()][
                        'series_uid'].values[0]
                self._series_pase_df = self.series_df.loc[
                    (self.series_df['study_uid'] == self.study_uid) & (self.series_df['series_uid'] == self.series_uid)]
            else:
                self._series_pase_df = self.series_df[self.series_df['series_uid'] == self.series_uid]
                assert (self._series_pase_df.shape[0] > 20)
                self.study_uid = self._series_pase_df['study_uid'].values[0]
            self._series_pase_df = self._series_pase_df.sort_values(by=['ImagePosition_Z']).reset_index(drop=True)
            self._series_pase_df = self._series_pase_df.fillna("NA")
            # create Dcm_real_series_paths
            self.Dcm_real_series_paths = self._series_pase_df['path'].values.tolist()
            self.image = self.create_images()
            print("Series_df init ok, success create series_real_df & Dcm_real_series_paths & Dcm_series_arr")
        except Exception as e:
            print("Series_df create failed %s" % e)
            raise ValueError

    def create_images(self):
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(self.Dcm_real_series_paths)
        image = reader.Execute()
        return image

    def _get_attr(self, obj, attr):
        return getattr(obj, attr, None)

    def _getmetadata(self, ds, keys, key):
        if key in keys:
            return ds.GetMetaData(key)
        else:
            return None

    @property
    def SOPClassUID(self):
        return self._series_pase_df.loc[0, 'SOPClassUID']

    @property
    def PatientID(self):
        return self._series_pase_df.loc[0, 'PatientID']

    @property
    def PatientName(self):
        return self._series_pase_df.loc[0, 'PatientName']

    @property
    def PatientBirthDate(self):
        return self._series_pase_df.loc[0, 'PatientBirthDate']

    @property
    def PatientSex(self):
        return self._series_pase_df.loc[0, 'PatientSex']

    @property
    def InstitutionName(self):
        return self._series_pase_df.loc[0, 'InstitutionName']

    @property
    def Manufacturer(self):
        return self._series_pase_df.loc[0, 'Manufacturer']

    @property
    def StudyDate(self):
        return self._series_pase_df.loc[0, 'StudyDate']

    @property
    def AcquisitionTime(self):
        return self._series_pase_df.loc[0, 'AcquisitionTime']

    @property
    def Access_num(self):
        return self._series_pase_df.loc[0, 'access_num']

    @property
    def Dcm_series_arr(self):
        return sitk.GetArrayFromImage(self.image)

    @property
    def Dcm_series_spacing(self):
        space_z = abs(self._series_pase_df.loc[0, 'ImagePosition_Z'] - self._series_pase_df.loc[1, 'ImagePosition_Z'])
        return self.image.GetSpacing()[:2] + (space_z,)
        # return self.image.GetSpacing()

    @property
    def Dcm_series_zup(self):
        diff = self._series_pase_df.loc[1, 'ImagePosition_Z'] - self._series_pase_df.loc[0, 'ImagePosition_Z']
        if diff > 0:
            return 1
        else:
            return 0

    @property
    def Dcm_series_instanceup(self):
        diff = self._series_pase_df.loc[1, 'instance_num'] - self._series_pase_df.loc[0, 'instance_num']
        if diff > 0:
            return 1
        else:
            return 0

    @property
    def Dcm_series_origin(self):
        return self.image.GetOrigin()

    @property
    def Dcm_series_size(self):
        return self.image.GetSize()

    @property
    def Dcm_series_direction(self):
        return self.image.GetDirection()

    @property
    def Dcm_series_position(self):
        return self._series_pase_df.loc[0, 'PatientPosition']


if __name__ == "__main__":
    # example
    Seriespath_candidates = [
        '/home/diannei/Workspace/ai-eyes-care/nodule_detect/dn_report/1526135486@hcYTb4JJFK.zip/dicom']

    s_df = Series(Seriespath_candidates, None, None)
    print(s_df._series_pase_df.shape)
    s_df._series_pase_df.to_csv(
        "/home/diannei/Workspace/ai-eyes-care/nodule_detect/dn_report/1526135486@hcYTb4JJFK.zip/test.csv", index=None)
    print(s_df.study_uid)
    print(s_df.series_uid)
