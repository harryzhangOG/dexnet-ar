void aruco() {
    cv::Mat cameraMatrix_, distCoeff_;
    cv::Ptr<cv::aruco::Dictionary> dictionary_{cv::aruco::getPredefinedDictionary(cv::aruco::DICT_4X4_100)};
    cv::Ptr<cv::aruco::DetectorParameters> parameters_{cv::aruco::DetectorParameters::create()};
    std::vector<std::vector<cv::Point2f>> corners_, rejected_;
    std::vector<int> ids_;
    float markerLength_{0.033f};
    std::vector<cv::Vec3d> rVecs_, tVecs_;

    // build the camera matrix from the camera intrinsics (provided elsewhere)
    cameraMatrix_ = cv::Mat::zeros(3, 3, CV_32F);
    cameraMatrix_.at<float>(0,0) = intrinsics.fx;
    cameraMatrix_.at<float>(1,1) = intrinsics.fy;
    cameraMatrix_.at<float>(0,2) = intrinsics.ppx;
    cameraMatrix_.at<float>(1,2) = intrinsics.ppy;
    cameraMatrix_.at<float>(2,2) = 1.0f;

    distCoeff_ = cv::Mat::zeros(5, 1, CV_32F);
    for (int i=0 ; i<5 ; ++i)
        distCoeff_.at<float>(i) = intrinsics.coeffs[i];

    // wrap the image (in ir) in a cv:Mat, and run ArUco detection
    cv::Mat image(ir.get_height(), ir.get_width(), CV_8UC1, (void*)ir.get_data());
    cv::aruco::detectMarkers(image, dictionary_, corners_, ids_, parameters_, rejected_, cameraMatrix_, distCoeff_);

    // check if no aruco markers were found
    if (ids_.empty())
        return;

    // estimate 3D poses of markers, storing rotations in rVecs and translations in tVecs
    cv::aruco::estimatePoseSingleMarkers(corners_, markerLength_, cameraMatrix_, distCoeff_, rVecs_, tVecs_);

    // convert each rotation and translation into a 4x4 matrix
    for (std::size_t i=0 ; i<ids_.size() ; ++i) {
        Eigen::Isometry3d t = Eigen::Isometry3d::Identity();
        for (int j=0 ; j<3 ; ++j)
            t(j,3) = tVecs_[i][j];

        cv::Rodrigues(rVecs_[i], axes_);
        for (int j=0 ; j<3 ; ++j)
            for (int k=0 ; k<3 ; ++k)
                t(j,k) = axes_.at<double>(j, k);

        // t is now a 4x4 matrix with the transform to the ArUco marker
    }
}
